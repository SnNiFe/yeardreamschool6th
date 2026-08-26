import {Pagination, Stack} from "@mui/material";
import Image from 'next/image';
import Link from "next/link";

export default function ListComp ({board, onSubmit}){

    let content = board.list.length === 0 ?
        <tr><th colSpan={6}>작성된 글이 없습니다.</th></tr>
        : board.list.map((item)=>(<tr key={item.idx}>
            <td>{item.idx}</td>
            <td>
                {item.cnt === 0 ? <Image src="/noimage.png" width={25} height={25} alt={"이미지없음"}/>
                    :<Image src="/image.png" width={25} height={25} alt={"이미지있음"}/>}
            </td>
            <td>
                <Link href={`/detail/${item.idx}`}>{item.subject}</Link>
            </td>
            <td>{item.user_name}</td>
            <td>{item.bHit}</td>
            <td>{item.reg_date}</td>
        </tr>));

    return (
        <>
            {content}
            <tr>
                <th colSpan={6}>
                    <div style={{justifyContent:'center', display:'flex'}}>
                        <Stack>
                            <Pagination
                                count={board.pages} // 전체 페이지 수
                                color={'primary'} // 선택한 색
                                variant={'outlined'}
                                shape={'rounded'}
                                siblingCount={2} // 중간정도 왔을때 양쪽에 표시할 개수
                                onChange={function(evt,page){
                                    //console.log(evt,page);
                                    //location.href='/list/'+page;
                                    onSubmit(page);
                                }}
                            />
                        </Stack>
                    </div>
                </th>
            </tr>
        </>
    );
}