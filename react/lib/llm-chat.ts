const streamQuestion = async (query: string, chatId: string) => {
  const response = await fetch('http://api-url/chat/query/stream', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
    //   'Authorization': `Bearer ${token}` 
    },
    body: JSON.stringify({ 
      query: query, 
      chat_id: chatId, 
      include_user_collection: true,
      use_official: true
    })
  });
 
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
 
  if (reader) {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      // Affichage progressif du chunk dans l'interface
      console.log(chunk); 
    }
  }
};
