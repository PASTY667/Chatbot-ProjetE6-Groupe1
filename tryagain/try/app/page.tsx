import { getServerSession } from "next-auth";
import Login from "@/app/login/page";
import SessionBanner from "@/app/service-banner";

export default async function Home() {
  const session = await getServerSession();

  if (!session || !session.user) {
    return <Login />;
  }

  return (
    <div style={{height: '100%'}}>
      <div style={{justifyContent:"top"}}><SessionBanner /></div>
      <div style={{justifySelf: "center", color: "white"}}>Bienvenue {session.user.name}</div>
    </div>
  );
}
