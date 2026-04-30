import style from "@/app/(user)/settings/settings.module.css";

export default function Settings() {
  return (
    <div className={style.settings}>
      <h1 className={style.settingsTitle}>Paramètres</h1>
      <div className={style.settingsSection}>
        <h4 className={style.settingUsername}>Nom d'utilisateur</h4>
        <input className={style.settingsInput} type="text" />
        <h4 className={style.settingsUploads}>Fichiers importés</h4>
        <div></div>
      </div>
    </div>
  );
}
