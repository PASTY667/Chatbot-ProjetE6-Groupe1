"use client";
import User from "@/app/user/page";
import Sidebar from "@/components/sidebar/sidebar";

export default function Home(){
    return(
      <>
      <Sidebar />
      <User />
      </>
    );
}