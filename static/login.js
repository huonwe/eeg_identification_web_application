function Login() {
    // id = document.getElementById('id').value
    password = document.getElementById('password').value
    if(password === ''){
        document.querySelector('.logintips').innerHTML = 'YOU HAVE NOT INPUT CID OR PASSWORD'
        return;
    }

    var data = {
        // 'id':id,
        'password':password
    }
    let formData = new FormData()
    // formData.append('id',id)
    formData.append('password',password)
    fetch('/login',{
        method: "POST",
        body: formData
    }).then((res=>{
        res.text().then((res)=>{
            console.log(res)
            if(res !='登陆失败'){
                location.href = '/index'
            }else {
                alert(res)
            }
        })
    }))

}