function eegDelete(name){
    if(confirm("Delete user "+name+" ?")){
        fetch("/delete?username="+name).then(data=>data.text()).then(data=>{
            resp = JSON.parse(data)
            alert(resp['msg'])
            fetch("/views/list?username=&status=").then(data=>data.text()).then(data=>{
                gates.mainContent.innerHTML = data
            })
        }).catch(e=>console.log(e))
    }
}

var eegNewHtml
function eegNew(){
    let mask = document.getElementById("mask")
    mask.style.display = "block"
    let box = document.createElement("div")
    // box.style.top = (document.body.clientHeight-box.offsetHeight)/2 + "px";
    // box.style.left = (document.body.clientWidth-box.offsetWidth)/2 + "px";
    // box.style.position = "absolute"
    // box.style.width = "100%"
    // box.style.height = "100%"
    // box.style.zIndex = "11"
    
    let xhr = new XMLHttpRequest()
    xhr.open("GET","/static/html/eegNew.html")
    xhr.send()
    xhr.onreadystatechange = ()=>{
        if((xhr.status>=200 && xhr.status<300)||xhr.status===304){
            let resp = xhr.response
            box.innerHTML = resp
            mask.appendChild(box)
        }
    }
}

function eegSort(){
    let mask = document.getElementById("mask")
    mask.style.display = "block"
    let box = document.createElement("div")
    let xhr = new XMLHttpRequest()
    xhr.open("GET","/static/html/eegSort.html")
    xhr.send()
    xhr.onreadystatechange = ()=>{
        if((xhr.status>=200 && xhr.status<300)||xhr.status===304){
            let resp = xhr.response
            box.innerHTML = resp
            mask.appendChild(box)
        }
    }
}

function eegSearch(name){
    var e = window.event || arguments.callee.caller.arguments[0];
    if(e.keyCode===13){
        fetch("/views/list?username="+name+"&status=").then(data=>data.text()).then(data=>{
            gates.mainContent.innerHTML = data
        })
    }
}

function eegStatusToggle(that,name){
    fetch("/switchStatus?username="+name).then(resp=>resp.text()).then(resp=>{
        // console.log(resp)
        resp = JSON.parse(resp)
        parent = that.parentNode.parentNode
        parent.childNodes[5].innerHTML = resp.data
        
    })
}

function eegMap(name){
    fetch("/views/map?username="+name).then(data=>data.text()).then(data=>{
        let mask = document.getElementById("mask")
        mask.style.display = "block"
        mask.innerHTML = data
    })
}


var mousedown = false
var scal = 1
function selfZoom(that){
    var ev = window.event || arguments.callee.caller.arguments[0];
    var down = true; // 定义一个标志，当滚轮向下滚时，执行一些操作
      down = ev.wheelDelta ? ev.wheelDelta < 0 : ev.detail > 0;
      if (!down) {
        // console.log('鼠标滚轮向上放大---------')
        scal = (parseFloat(scal) + 0.05).toFixed(2);
        // console.log("放大系数: " + scal)
        that.style.transform = "scale(" + scal + ")"; //scale()在这里要使用拼接的方式才能生效
        // wall.style.transformOrigin = '0 0';
        that.style.transformOrigin = "50% 50%";
      } else {
        // console.log('鼠标滚轮向下缩小++++++++++')
        if (scal == 0.1) {
          scal = 0.1;
          return;
        } else {
          scal = (parseFloat(scal) - 0.05).toFixed(2);
        }
        // console.log("缩小系数: " + scal)
        that.style.transform = "scale(" + scal + ")"; //scale()在这里要使用拼接的方式才能生效。
        that.style.transformOrigin = "50% 50%";
      }
}

function selfMove(that){
    if (mousedown) {
        var e = window.event || arguments.callee.caller.arguments[0];
        console.log(e)
        that.style.left =
          parseInt(that.style.left.replace("px", "")) + e.movementX + "px";
          that.style.top =
          parseInt(that.style.top.replace("px", "")) + e.movementY + "px";
      }
}