export default function PhotosComp ({photos,ip}){
    console.log(photos);

    return photos.map(photo=>
        <div key={photo.file_idx}>
            <p><img src={`${ip}/photo/${photo.file_idx}`} width={300} alt={photo.ori_filename}/></p>
            <a href={`${ip}/download/${photo.file_idx}`}>다운로드</a>
        </div>
    );
}