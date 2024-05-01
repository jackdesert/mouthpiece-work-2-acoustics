
function copyLinkToClipboard(event) {
    let clickedElement = event.target,
        parentElement = clickedElement.parentElement,
        parentId = parentElement.id,
        textArea = document.createElement('textarea'),
        // Use origin + pathname to skip any extant hashtags
        currentHref = window.location.origin + window.location.pathname ,
        link = `${currentHref}#${parentId}`,
        afterClickMessage = 'Copied to clipboard'

  textArea.value = link
  document.body.appendChild(textArea)
  textArea.select()
  document.execCommand('copy')
  document.body.removeChild(textArea)
  clickedElement.innerHTML = afterClickMessage

  // Let user know that we've put it on the clipboard
  setTimeout(function(){
      clickedElement.innerHTML = ''
  }, 5000)
}


var bindShareLinks = function(){
    var elements = document.querySelectorAll('.message__share-icon')
    elements.forEach(function(e){
        e.addEventListener('click', copyLinkToClipboard)
    })
}


bindShareLinks()
