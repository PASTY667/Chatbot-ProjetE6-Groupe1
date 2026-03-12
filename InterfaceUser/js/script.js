//Affichage du nom du pdf importé
const uploadFile = document.getElementById('upload-file');
const fileName = document.getElementById('file-name');
 
uploadFile.addEventListener('change', (e) => {
  const selectedFile = e.target.files[0];
  if (selectedFile) {
    fileName.textContent = selectedFile.name;
  }
});