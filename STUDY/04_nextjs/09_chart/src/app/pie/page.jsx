'use client'
import {PieChart} from "@mui/x-charts";

export default function PieChartPage(){
    return(
        <>
            <div>
                <PieChart
                    series={[
                        {data:[
                                {value:10,label:'A 영역'},
                                {value:15,label:'B 영역'},
                                {value:20,label:'C 영역'},
                                {value:55,label:'D 영역'},
                            ]}
                    ]}
                    width={400}
                    height={200}
                />
            </div>
            <div>
                <PieChart
                    series={[
                        {data:[
                                {value:10,label:'A 영역'},
                                {value:15,label:'B 영역'},
                                {value:20,label:'C 영역'},
                                {value:55,label:'D 영역'},
                            ],
                            innerRadius:20, // 파이차트 안쪽 구멍
                            outerRadius:100, // 외각 크기 (outer-inner = 보여지는 파이)
                            paddingAngle:5, // 파이 영역간 간격
                            cornerRadius:10, // 파이 모서리 둥글기 정도
                            startAngle:30, // 시작 각도 (0이 기준)
                            endAngle:390, // 종료 각도 (360이 기준)
                            arcLabel:function(item){
                            //console.log(item);
                            return `${item.label} : ${item.value}`;
                            }
                        }
                    ]}
                    width={400}
                    height={200}
                />
            </div>
            <div>
                <PieChart
                    series={[
                        {data:[
                                {value:10,label:'A 영역'},
                                {value:15,label:'B 영역'},
                                {value:20,label:'C 영역'},
                                {value:55,label:'D 영역'},
                            ],
                            arcLabel:item=> `${item.value}%`,
                            highlightScope:{highlight:'item',fade:'global'},
                            faded:{ // fade 에 대한 효과
                                color:'gray',
                                innerRadius:50,
                                additionalRadius:-30,
                            }
                        }
                    ]}
                    width={400}
                    height={200}
                    onItemClick={(evt,data)=>console.log(evt,data)}
                />
            </div>
        </>
    );
}