import style from "@/components/Upload/upload.module.css";
import Image, { StaticImageData } from "next/image";

type InputProps = {
    image: string | StaticImageData;
    label: string;
};

export default function Input({image, label,}:InputProps){
    return(
        <div className="uploadDisplay">
            <Image src={image} alt="" />
            <span className={style.uploadTitle}>{label}</span>
        </div>
    )
}