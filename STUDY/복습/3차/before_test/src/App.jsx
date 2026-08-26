import React, { useState } from 'react'

function App() {

  const answer = 'hi';

  // a_1
  let scores = [88, 92, 75, 100, 64];
  let fruitNames = ["apple", "banana", "cherry", "durian"];
  let isCompletedList = [true, false, false, true, true];
  let prices = [1500, 3000, 4500, 2200, 800, 12000];
  let userIDs = ["user01", "user02", "admin", "guest99", "tester"];

  const a_1 = function(){
    for(let i=0; i<userIDs.length; i++){
      console.log(userIDs[i]);
    }
    console.log('----');
  }
  // a_2
  let countdown = [1, 2, 3, 4, 5];
  let history = ["home", "about", "products", "cart", "checkout"];
  let stackData = [101, 202, 303, 404];
  let logMessages = ["INFO: Start", "WARN: Slow network", "ERROR: Timeout"];
  let dailyTemperatures = [23.5, 25.1, 22.0, 21.8, 26.4, 27.0];

  const a_2 = function(){
    for(let i=dailyTemperatures.length-1; i>=0;i--){
      console.log(dailyTemperatures[i]);
    }
    console.log('----');
  }
  //a_3
  let numbers = [10, 20, 30, 40, 50, 60, 70, 80];

  const a_3 = function(){
    for(let i=0;i<numbers.length;i++){
      if(i%2===0){
        console.log(numbers[i]);
      }
    }
    console.log('----');
  }
  //a_4
  let numbersList = [5, 10, 15, 20, 25, 30, 35, 40];
  const a_4 = function(){
    for(let i=0;i<numbersList.length;i++){
      if(i>=2 && i<=5){
        console.log(numbersList[i]);
      }
    }
    console.log('----');
  }
  //b_1
  let word = "JAVASCRIPT";
  const b_1 = function(){
    for(let i=0;i<word.length;i++){
        console.log(word[i]);
    }
    console.log('----');
  }
  //b_2
  //b_3
  let fullText = "DEVELOPER";
  let pattern = "A1B2C3D4E5";
  const b_3 = function(){
    for(let i=0;i<pattern.length;i++){
      if(/[0-9]/.test(pattern[i])){
        console.log(pattern[i]);
      }
    }
    console.log('----');
  }
  //c_1
  let studentProfile = { name: "김철수", age: 20, major: "컴퓨터공학" };
  const c_1 = function(){
    console.log(Object.keys(studentProfile));
    let ar = Object.keys(studentProfile);
    for(let i=0; i<ar.length; i++){
      console.log(studentProfile[ar[i]]);
    }
    console.log('----');
  }
  //c_2
  let users = [{name: "Alice"}, {name: "Bob"}, {name: "Charlie"}];
  const c_2 = function(){
    for(let i=0; i<users.length; i++){
      console.log(users[i]['name']);
    }
    console.log('----');
  }
  //c_3
  let matrix = [[1, 2], [3, 4], [5, 6]];
  const c_3 = function (){
    for(let i=0;i<matrix.length;i++){
      for(let j=0;j<matrix[i].length;j++){
        console.log(matrix[i][j]);
      }
    }
    console.log('----');
  }
  //

  //A-3-1 (짝수 인덱스 순회)
  let anumbers = [10, 20, 30, 40, 50, 60, 70, 80];
  for (let i = 0; i < anumbers.length; i += 2) {
    console.log(anumbers[i]);
  }


  //C-2-5 (객체 배열 접근)
  let bstudents = [{name: "김민수", score: 85}, {name: "이영희", score: 92}, {name: "박준형", score: 78}];
  for (let i = 0; i < bstudents.length; i++) {
    console.log(bstudents[i].name + " : " + bstudents[i].score + "점");
  }


  //C-3-1 (2차원 배열 중첩 for문)
  let cmatrix = [[1, 2], [3, 4], [5, 6]];
  for (let i = 0; i < cmatrix.length; i++) {
    for (let j = 0; j < cmatrix[i].length; j++) {
      console.log(cmatrix[i][j]);
    }
  }

  // console.log('--1 end--');

  return (
    <>
      <h1>JS 복습 1단계 : 데이터 접근하기</h1>
      <p>{answer}</p>
      {/*<p>{a_1()}</p>*/}
      {/*<p>{a_2()}</p>*/}
      {/*<p>{a_3()}</p>*/}
      {/*<p>{a_4()}</p>*/}
      {/*<p>{b_1()}</p>*/}
      {/*<p>{b_3()}</p>*/}
      {/*<p>{c_1()}</p>*/}
      {/*<p>{c_2()}</p>*/}
      {/*<p>{c_3()}</p>*/}
    </>
  )
}

export default App
