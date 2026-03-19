import style from "@/app/history/history.module.css";

export default function History(){
    return (
        <div className={style.historyPage}>
        <h1 className={style.historyTitle}>Historique</h1>
        <div className={style.historySection}>
            <div className={style.searchbar}>
                {/* <input className={style.searchbarInput} type="text" value="Chercher une conversation"> */}
            </div>
            <div className={style.historyContent}>
                <div className={style.component}>
                    <h4 className={style.compotentTitle}>Titre</h4>
                    <p className={style.componentText}>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                </div>
            </div>
        </div>
    </div>
    )
}