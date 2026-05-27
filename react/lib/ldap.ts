import { createClient } from "ldapjs";

const LDAP_URL = process.env.LDAP_URL!;
const BASE_DN = process.env.LDAP_BASE_DN!;

export async function authenticateLDAP(username: string, password: string) {
  const client = createClient({ url: LDAP_URL });

  return new Promise((resolve) => {
    try {
      // 1. Bind avec UPN
      const upn = `${username}@franklin.llm`;

      console.log("Trying LDAP bind for:", username);

      client.bind(upn, password, (err) => {
        if (err) {
          console.error("LDAP bind error:", err);
          client.unbind();
          resolve(null);
          return;
        }

        // 2. Recherche utilisateur
        client.search(BASE_DN, {
          scope: "sub",
          filter: `(sAMAccountName=${username})`,
          attributes: ["cn", "mail", "memberOf", "sAMAccountName", "userPrincipalName"],
        }, (err, res) => {
          if (err) {
            console.error("LDAP search error:", err);
            client.unbind();
            resolve(null);
            return;
          }

          let user: any = null;
          const entries: any[] = [];

          res.on("searchEntry", (entry) => {
            entries.push(entry.object);
          });

          res.on("error", (err) => {
            console.error("LDAP search stream error:", err);
          });

          res.on("end", () => {
            user = entries[0];
            console.log("LDAP search result:", entries);
            console.log("USER FOUND:", user);

            if (!entries.length || !user) {
              client.unbind();
              resolve(null);
              return;
            }

            // 3. Groupes
            const rawGroups = user.memberOf
              ? Array.isArray(user.memberOf)
                ? user.memberOf
                : [user.memberOf]
              : [];

            const groups = rawGroups.map((g: any) =>
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

            client.unbind();

            resolve({
              id: String(user.sAMAccountName),
              name: String(user.cn),
              email,
              role,
              groups,
            });
          });
        });
      });
    } catch (err) {
      console.error("LDAP error FULL:", JSON.stringify(err, null, 2));
      console.log("LDAP URL:", LDAP_URL);
      console.log("BASE DN:", BASE_DN);
      client.unbind();
      resolve(null);
    }
  });
}