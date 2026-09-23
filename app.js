fetch('/data/clips.json').then(r=>r.json()).then(d=>console.log('RCD clips loaded', d.clips?.length||0));
