'use client'
import {BarChart} from "@mui/x-charts";

export default function BarChartPage(){
    return(
        <>
            <div style={{width:"30%"}}>
                <BarChart
                    series={[
                        {data:[4,2,3,5],label:'성장률'}
                    ]} /*막대그래프 하나하나의 내용*/
                    xAxis={[
                        {data:['1분기','2분기','3분기','4분기'],scaleType:'band'}
                    ]} /*x 축의 내용*/
                    width={500}
                    height={300}
                    barLabel={'value'} /*bar 에 표시 될 내용*/
                    borderRadius={10}
                    grid={{horizontal:true}}
                />
            </div>
            <div style={{width:"30%"}}>
                <BarChart
                    series={[
                        {data:[4,2,3,5],label:'매출'},
                        {data:[3,1,3,4],label:'순익'},
                        {data:[2,2,5,6],label:'방문객'}
                    ]} /*막대그래프 하나하나의 내용*/
                    xAxis={[
                        {data:['1분기','2분기','3분기','4분기'],scaleType:'band'}
                    ]} /*x 축의 내용*/
                    width={500}
                    height={300}
                    barLabel={'value'} /*bar 에 표시 될 내용*/
                    borderRadius={10}
                    grid={{horizontal:true}}
                />
            </div>
            <div style={{width:"30%"}}>
                <BarChart
                    /*stack 의 이름이 같은 그래프 끼리 쌓이게 된다.*/
                    series={[
                        {data:[4000,3000,2000,2780],label:'pv',stack:'stack1'},
                        {data:[2400,1398,9800,3908],label:'uv',stack:'stack1'}
                    ]}
                    xAxis={[
                        {data:['1분기','2분기','3분기','4분기'],scaleType:'band'}
                    ]}
                    width={500}
                    height={300}

                />.
            </div>
        </>
    );
}