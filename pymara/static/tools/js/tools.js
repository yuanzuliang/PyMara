function go_to_login() {
    swal({
        title: '检测到您还未登录',
        text: '请前往登录',
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '登录',
    }).then(function () {
        location.href = htmlUrl + 'pymara/templates/user/login.html'
    })
}

function check_login() {
    $.ajax({
        url: baseUrl + "v1/index/judge_login",
        type: "post",
        dataType: "json",
        success: function (res) {
            if (res.code === 403) {
                location.href = htmlUrl + 'pymara/templates/user/login.html'
            } else if (res.code === 444) {
                swal("您的账号被限制", "请联系工作人员", "error")
            }
        },
        beforeSend: function (request) {
            request.setRequestHeader("pymaratoken", window.localStorage.getItem("pymara_token"));
        }
    })
}

function no() {
    swal('', '该功能正在努力开发中')
}

function go_to_index() {
    location.href = htmlUrl + 'pymara/templates/user/login.html'
}

function go_to_back() {
    history.back(-1)
}

