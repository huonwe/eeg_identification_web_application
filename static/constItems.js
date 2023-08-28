function jsonifyRes(res){
    if(typeof res == "object"){
        return res;
    }else {
        try{
            return JSON.parse(res)
        }catch (e) {
            return null;
        }
    }
}

function handleCode(jsonR) {
    if(typeof jsonR != 'object'){
        $('#RightContainer').html(jsonR)
    }
    let code = jsonR.code
    console.log(code)
    if (typeof code != 'string'){
        code = code.toString()
    }
    let code_1 = code.charAt(0)
    switch (code_1) {
        case '0':
            return ;
        case '1':
            alert(jsonR.msg);
            return ;
        case '2':
            alert(jsonR.msg);
            window.location.href=jsonR['url'];
            return ;
        case '4':
            if(code === 4001){
                window.open('/downloadfile?filepath='+jsonR.path)
            }
            return ;
    }
}

function resize_canvas(canvas,w,h)
{
    var nc = document.createElement("canvas");
    nc.width = canvas.width;
    nc.height = canvas.height;
    nc.getContext("2d").drawImage(canvas,0,0);
    canvas.width = w;
    canvas.height = h;
    ctx = canvas.getContext('2d')
    ctx.drawImage(nc,0,0);
}