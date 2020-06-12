<!-- 页面背景和猫头鹰 -->
$(function () {
    // 猫头鹰图片
    $("#psd").focus(function () {
        $("#psd-img").prop("src", "../../static/user/img/png/_psd_img.png")
    }).blur(function () {
        $("#psd-img").prop("src", "../../static/user/img/png/psd_img.png")
    });

    // 密码框小眼睛
    var showPsdI = 0;
    $("#showPsd").on("click", function () {
        if(showPsdI===0){
            $(this).prop("className", "glyphicon glyphicon-eye-open");
            $("#psd").prop("type", "text");
            showPsdI++;
        }else{
            $(this).prop("className", "glyphicon glyphicon-eye-close");
            $("#psd").prop("type", "password");
            showPsdI--;
        }
    })
});

