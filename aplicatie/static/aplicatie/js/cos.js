function getCos() {
    return JSON.parse(localStorage.getItem('cos')) || {};
}

function saveCos(cos) {
    localStorage.setItem('cos', JSON.stringify(cos));
    actualizeazaInterfata();

    if (document.getElementById("lista-cos")) {
        afiseazaCos();
    }
}

function actualizeazaInterfata() {
    let cos = getCos();
    
    document.querySelectorAll("[data-produs-id]").forEach(el => {
        let id = el.dataset.produsId;
        // Căutăm input-ul corespunzător acestui produs
        let inputNumeric = document.getElementById(`input-${id}`);
        
        if (cos[id]) {
            el.classList.add("in-cos");
            // Dacă produsul e în coș, punem cantitatea în pătrățel
            if (inputNumeric) {
                inputNumeric.value = cos[id].cantitate;
            }
        } else {
            el.classList.remove("in-cos");
            // Dacă nu e în coș, resetăm pătrățelul la 0
            if (inputNumeric) {
                inputNumeric.value = 0;
            }
        }
    });
}

function adaugaInCos(id, stoc, pret, nume, imagine) {
    id = String(id);
    stoc = parseInt(stoc);
    let cos = getCos();

    if (!cos[id]) {
        cos[id] = { 
            cantitate: 0, 
            stoc: stoc, 
            pret: parseFloat(pret), 
            nume: nume,
            imagine: imagine
        };
    }

    if (parseInt(cos[id].cantitate) + 1 > stoc) {
        alert("Stoc epuizat!");
        return;
    }

    cos[id].cantitate++;
    saveCos(cos);
}

function creste(id, stoc, pret, nume, imagine) {
    id = String(id);
    stoc = parseInt(stoc); // Ne asigurăm că stocul e număr
    let cos = getCos();
    
    if (!cos[id]) {
        cos[id] = { cantitate: 0, stoc: stoc, pret: parseFloat(pret), nume: nume, imagine: imagine };
    }

    // Verificăm DACĂ adăugarea încă unei unități depășește stocul
    if (parseInt(cos[id].cantitate) + 1 > stoc) {
        alert("Nu poți adăuga mai mult decât stocul disponibil: " + stoc);
        return; // Oprim execuția AICI, deci nu mai face saveCos
    }

    cos[id].cantitate++;
    saveCos(cos);
}

function scade(id) {
    id = String(id);
    let cos = getCos();
    
    if (!cos[id]) return; // Nu avem ce scădea dacă nu e în coș

    cos[id].cantitate--;
    if (cos[id].cantitate <= 0) {
        delete cos[id];
    }
    saveCos(cos);
}

function seteazaCantitate(id, valoare, stoc) {
    id = String(id);
    valoare = parseInt(valoare);
    
    if (isNaN(valoare) || valoare < 1) {
        let cos = getCos();
        delete cos[id];
        saveCos(cos);
        return;
    }

    if (valoare > stoc) {
        alert("Depășești stocul!");
        return;
    }

    let cos = getCos();
    cos[id] = { cantitate: valoare, stoc: stoc };
    saveCos(cos);
}

document.addEventListener("DOMContentLoaded", actualizeazaInterfata);


// COS.HTML

function afiseazaCos(sortare = "nume") {
    let cos = getCos();
    let container = document.getElementById("lista-cos");
    container.innerHTML = "";

    let produse = Object.entries(cos);

    if (sortare === "nume") {
        produse.sort((a, b) => a[0].localeCompare(b[0]));
    } else {
        produse.sort((a, b) => a[1].pret - b[1].pret);
    }

    let totalPret = 0;
    let totalProduse = 0;

    produse.forEach(([id, p]) => {
        let subtotal = p.pret * p.cantitate;
        totalPret += subtotal;
        totalProduse += p.cantitate;
        let fallbackImg = "/static/aplicatie/imagini/WheyProteinChoco5kg.png";

        container.innerHTML += `
            <div class="card-produs">
                <h3>
                    <a href="/produse/${id}/">${p.nume ? p.nume : 'Produs ' + id}</a>
                </h3>

                <img src="${p.imagine}" 
                 alt="${p.nume}" 
                 style="max-width:150px; border-radius:12px;" 
                 onerror="this.onerror=null; this.src='${fallbackImg}';">
                
                <p>Preț unitar: ${p.pret} RON</p>
                <p>Cantitate: ${p.cantitate}</p>
                <p>Subtotal: ${subtotal.toFixed(2)} RON</p>

                <button onclick="scade('${id}')">-</button>
                <button onclick="creste('${id}', ${p.stoc})">+</button>
                <button onclick="stergeProdus('${id}')">Șterge</button>
            </div>
        `;
    });

    document.getElementById("total-produse").innerText = totalProduse;
    document.getElementById("total-pret").innerText = totalPret.toFixed(2);
}

function stergeProdus(id) {
    let cos = getCos();
    delete cos[id];
    saveCos(cos);
    afiseazaCos();
}

function sorteazaCos(criteriu) {
    afiseazaCos(criteriu);
}

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("lista-cos")) {
        afiseazaCos();
    }
});


function cumpara() {
    let cos = getCos();

    if (Object.keys(cos).length === 0) {
        alert("Coșul este gol!");
        return;
    }

    fetch("/cumpara/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(cos)
    })
    .then(r => r.json())
    .then(data => {
        alert("Comanda a fost realizată cu succes!");
        localStorage.removeItem("cos");
        window.location.href = "/";
    });
}

// Adaugă asta la începutul sau finalul fișierului cos.js
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
