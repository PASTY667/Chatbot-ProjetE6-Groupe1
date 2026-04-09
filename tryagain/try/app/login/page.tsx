import style from "@/app/login/login.module.css"

export default function Login(){
    return(
        <div className={style.login}>
            <h1 className={style.headline}>Bienvenue!</h1>
            <div className={style.loginSection}>
                <h3 className={style.loginTitle}>Connexion</h3>
                <h5 className={style.loginText}>Nom d'utilisateur</h5>
                <input className={style.inputUser}/>
                <h5 className={style.loginText}>Mot de passe</h5>
                <input className={style.inputPwd} type="password"/>
                <div className={style.divButton}>
                    <button className={style.loginButton}>Se connecter</button>
                </div>
            </div>
        </div>
    )
}