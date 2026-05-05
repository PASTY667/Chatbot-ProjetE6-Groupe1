import { Client } from "ldapts";

const LDAP_URL = process.env.LDAP_URL!;
const BASE_DN = process.env.LDAP_BASE_DN!;

export async function authenticateLDAP(username: string, password: string) {
  const client = new Client({ url: LDAP_URL });

  try {
    // 1. Bind avec UPN
    const upn = `${username}@franklin.llm`;

    console.log("Trying LDAP bind for:", username);

    await client.bind(upn, password);

    // 2. Recherche utilisateur
    const { searchEntries } = await client.search(BASE_DN, {
      scope: "sub",
      filter: `(sAMAccountName=${username})`,
      attributes: ["cn", "mail", "memberOf", "sAMAccountName", "userPrincipalName"],
    });

    const user = searchEntries[0];

    console.log("LDAP search result:", searchEntries);
    console.log("USER FOUND:", user);

    if (!searchEntries.length) return null;
    if (!user) return null;

    // 3. Groupes
    const rawGroups = user.memberOf
  ? Array.isArray(user.memberOf)
    ? user.memberOf
    : [user.memberOf]
  : [];

const groups = rawGroups.map((g) =>
  typeof g === "string"
    ? g
    : Buffer.isBuffer(g)
      ? g.toString()
      : String(g)
);

const rawEmail = user.mail ?? user.userPrincipalName;

let email: string;

if (Array.isArray(rawEmail)) {
  email = String(rawEmail[0]);
} else if (Buffer.isBuffer(rawEmail)) {
  email = rawEmail.toString();
} else if (rawEmail) {
  email = String(rawEmail);
} else {
  email = "";
}

    // 4. rôle
    const role = groups.some((g) =>
      String(g).toLowerCase().includes("admin")
    )
      ? "admin"
      : "user";

    return {
  id: String(user.sAMAccountName),
  name: String(user.cn),
  email,
  role,
  groups, 
};

  } catch (err) {
    console.error("LDAP error FULL:", JSON.stringify(err, null, 2));
    console.log("LDAP URL:", LDAP_URL);
    console.log("BASE DN:", BASE_DN);
    return null;
  } finally {
    await client.unbind();
  }
}