'use client'
import {LineChart} from "@mui/x-charts";

export default function LineChartPage(){
    return(
        <>
            <div style={{width:"50%"}}>
                <LineChart
                    series={[
                        {data:[2,5.5,2,8.5,1,5],curve:'step'}
                    ]}
                    width={500}
                    height={300}
                    xAxis={[
                        {data:['1월','2월','3월','4월','5월','6월'],scaleType:'band'}
                    ]}
                    grid={{vertical:true,horizontal:true}}
                />
            </div>
            <div style={{width:"50%"}}>
                <LineChart
                    series={[
                        {data:[2,5.5,2,8.5,1,5],area:true,color:'red'}
                    ]}
                    width={500}
                    height={300}
                    xAxis={[
                        {data:[0,1,2,3,4,5]}
                    ]}
                    grid={{vertical:true,horizontal:true}}
                />
            </div>
            <div style={{width:"50%"}}>
                <LineChart
                    series={[
                        {data:[3,4,2,8,1,5],area:true,stack:'total',label:'A그룹',highlightScope:{highlight:'item'}},
                        {data:[4,3,1,5,2,6],area:true,stack:'total',label:'B그룹',highlightScope:{highlight:'item'}},
                        {data:[2,5,3,7,3,2],area:true,stack:'total',label:'C그룹',highlightScope:{highlight:'item'}},
                    ]}
                    width={500}
                    height={300}
                    xAxis={[
                        {data:['1월','2월','3월','4월','5월','6월'],scaleType:'band'}
                    ]}
                    grid={{vertical:true,horizontal:true}}
                    onAreaClick={(evt,data)=>console.log('a',evt,data)}
                    // onMarkClick={(evt,data)=>console.log('m',evt,data)}
                    // onLineClick={(evt,data)=>console.log('l',evt,data)}
                />
            </div>
        </>
    );
}