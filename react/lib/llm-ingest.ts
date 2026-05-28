const uploadDocument = async (file: File, chatId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('scope', 'user'); // 'user' ou 'official'
  formData.append('chat_id', chatId); // Identifiant de la session utilisateur
 
  const response = await fetch('http://api-url/ingest/upload', {
    method: 'POST',
    headers: { 
    //   'Authorization': `Bearer ${token}` 
    },
    body: formData
  });
  return await response.json();
};
