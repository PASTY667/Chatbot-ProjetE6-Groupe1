import mysql, { type Pool, type RowDataPacket } from "mysql2/promise";

export type StoredChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type StoredChatSession = {
  id: string;
  title: string;
  messages: StoredChatMessage[];
};

type SessionRow = RowDataPacket & {
  id: string;
  title: string;
};

type MessageRow = RowDataPacket & StoredChatMessage & {
  session_id: string;
};

let pool: Pool | null = null;
let initialized: Promise<void> | null = null;

function getPool() {
  if (!process.env.DATABASE_URL) {
    throw new Error("DATABASE_URL is not configured");
  }

  pool ??= mysql.createPool(process.env.DATABASE_URL);
  return pool;
}

async function ensureTables() {
  const db = getPool();

  await db.execute(`
    CREATE TABLE IF NOT EXISTS frontend_chat_session (
      id VARCHAR(120) PRIMARY KEY,
      user_login VARCHAR(120) NOT NULL,
      title VARCHAR(160) NOT NULL,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_frontend_chat_session_user_updated (user_login, updated_at)
    )
  `);

  await db.execute(`
    CREATE TABLE IF NOT EXISTS frontend_chat_message (
      id VARCHAR(160) PRIMARY KEY,
      session_id VARCHAR(120) NOT NULL,
      role VARCHAR(20) NOT NULL,
      content TEXT NOT NULL,
      sort_order INT NOT NULL,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_frontend_chat_message_session_order (session_id, sort_order),
      CONSTRAINT fk_frontend_chat_message_session
        FOREIGN KEY (session_id)
        REFERENCES frontend_chat_session(id)
        ON DELETE CASCADE
    )
  `);
}

async function getDb() {
  initialized ??= ensureTables();
  await initialized;
  return getPool();
}

export async function listChatSessions(userLogin: string): Promise<StoredChatSession[]> {
  const db = await getDb();

  const [sessionRows] = await db.execute<SessionRow[]>(
    `
      SELECT id, title
      FROM frontend_chat_session
      WHERE user_login = ?
      ORDER BY updated_at DESC
    `,
    [userLogin],
  );

  if (sessionRows.length === 0) {
    return [];
  }

  const sessionIds = sessionRows.map((session) => session.id);
  const placeholders = sessionIds.map(() => "?").join(",");
  const [messageRows] = await db.query<MessageRow[]>(
    `
      SELECT session_id, id, role, content
      FROM frontend_chat_message
      WHERE session_id IN (${placeholders})
      ORDER BY sort_order ASC, created_at ASC
    `,
    sessionIds,
  );

  const messagesBySession = new Map<string, StoredChatMessage[]>();
  for (const message of messageRows) {
    const messages = messagesBySession.get(message.session_id) ?? [];
    messages.push({
      id: message.id,
      role: message.role,
      content: message.content,
    });
    messagesBySession.set(message.session_id, messages);
  }

  return sessionRows.map((session) => ({
    id: session.id,
    title: session.title,
    messages: messagesBySession.get(session.id) ?? [],
  }));
}

export async function createChatSession(userLogin: string, id: string, title: string) {
  const db = await getDb();

  await db.execute(
    `
      INSERT INTO frontend_chat_session (id, user_login, title)
      VALUES (?, ?, ?)
      ON DUPLICATE KEY UPDATE title = VALUES(title), updated_at = CURRENT_TIMESTAMP
    `,
    [id, userLogin, title],
  );
}

export async function renameChatSession(userLogin: string, id: string, title: string) {
  const db = await getDb();

  await db.execute(
    `
      UPDATE frontend_chat_session
      SET title = ?, updated_at = CURRENT_TIMESTAMP
      WHERE id = ? AND user_login = ?
    `,
    [title, id, userLogin],
  );
}

export async function replaceChatMessages(
  userLogin: string,
  sessionId: string,
  messages: StoredChatMessage[],
) {
  const db = await getDb();
  const connection = await db.getConnection();

  try {
    await connection.beginTransaction();
    const [sessions] = await connection.execute<SessionRow[]>(
      "SELECT id FROM frontend_chat_session WHERE id = ? AND user_login = ? LIMIT 1",
      [sessionId, userLogin],
    );

    if (sessions.length === 0) {
      throw new Error("Chat session not found");
    }

    await connection.execute("DELETE FROM frontend_chat_message WHERE session_id = ?", [sessionId]);

    for (const [index, message] of messages.entries()) {
      await connection.execute(
        `
          INSERT INTO frontend_chat_message (id, session_id, role, content, sort_order)
          VALUES (?, ?, ?, ?, ?)
        `,
        [message.id, sessionId, message.role, message.content, index],
      );
    }

    await connection.execute(
      "UPDATE frontend_chat_session SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
      [sessionId],
    );
    await connection.commit();
  } catch (error) {
    await connection.rollback();
    throw error;
  } finally {
    connection.release();
  }
}
