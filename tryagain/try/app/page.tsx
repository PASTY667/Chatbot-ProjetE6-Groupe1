import { getServerSession } from "next-auth";
import Login from "@/app/login/page";

export default async function Home() {
  const session = await getServerSession();

  if (!session || !session.user) {
  return <Login />;
}

return <div>Bienvenue {session.user.name}</div>;
}