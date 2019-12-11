function copy2clipboard(note) {
    console.log(note)
    let textarea = document.createElement('textarea')
    textarea.id = 't'
    textarea.style.height = 0
    document.body.appendChild(textarea)
    textarea.value = document.getElementById("geo_uri").innerText
    let selector = document.querySelector('#t')
    selector.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    document.getElementById("copy_button").innerText = note
    setTimeout(function() {
        document.getElementById("copy_button").innerText = ""
    }, 1000);
}