// src/App.jsx (수정 불가)
import React from 'react';
import Book from './Book';

function App() {
  return (
    <div>
      <Book title="해리포터" />
      <Book title="어린왕자" />
    </div>
  );
}

// export default App;

// src/Book.jsx
import React from 'react';

/* 코드를 작성하세요. */
function Book({title}){
    return(
        <h2>도서명 : [{title}]</h2>
    );
}
// export default Book;