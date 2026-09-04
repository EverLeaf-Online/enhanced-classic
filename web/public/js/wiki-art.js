(()=>{
  const markMissing=img=>{
    if(!(img instanceof HTMLImageElement))return;
    img.hidden=true;
    const frame=img.closest('.wikiMapleAsset');
    if(frame)frame.classList.add('is-missing');
  };

  const bind=img=>{
    if(!(img instanceof HTMLImageElement)||img.dataset.wikiArtBound==='1')return;
    img.dataset.wikiArtBound='1';
    img.addEventListener('error',()=>markMissing(img),{once:true});
    if(img.complete&&img.naturalWidth===0)markMissing(img);
  };

  document.querySelectorAll('img[data-wiki-art]').forEach(bind);
})();
