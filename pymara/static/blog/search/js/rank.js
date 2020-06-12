$(
    //页面跳转
    $('.home_log').on('click', function () {
        location.href = '#'
    }),
    $('.rank_log').on('click', function () {
        location.href = BLOGHREF + '/rank.html'
    }),
    //跳转搜索界面
    $('#search').on('click', function () {
        // localStorage.setItem('keyword',$('#keyword').val())
        //获取搜索框内容存入session
        sessionStorage.setItem('keyword', $('#keyword').val())
        location.href = BLOGHREF + '/search.html'
    }),

    function get_blog_infos(blog_ids) {
        $.ajax({
            url: URL + '/v1/search/rank',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify(blog_ids),
            success: function (res) {
                if (res.code === 200) {
                    page = sessionStorage.getItem('rank_page')
                    sessionStorage.setItem('rank_page', page + blog_ids.length)
                    $.each(res.data, function (index, obj) {
                        html = '<li>\n' +
                            '    <a href="' + obj.abstract + '" class="title" target="_blank" >' + obj.title + '</a>\n' +
                            '    <span class="abstract">' + obj.abstract + '</span>\n' +
                            '    <a href="#" class="name"><img src="../static/img/default.jpg" class="img-circle">' + obj.username + '</a>\n' +
                            '    <span class="history"><i class="glyphicon glyphicon-thumbs-up praise">' + obj.praise + '</i><i\n' +
                            '            class="glyphicon glyphicon-eye-open">' + obj.browse + '</i><i\n' +
                            '            class="glyphicon glyphicon-comment">' + obj.comment + '</i></span>\n' +
                            '</li>'
                        $('.info').append(html)
                    })
                }
            }
        })
    },
    function get_blog_ids(rule) {
        $.ajax({
            url: URL + '/v1/search/rank?rule=' + rule,
            type: 'get',
            dataType: 'json',
            success: function (res) {
                if (res.code === 200) {
                    sessionStorage.setItem('rank_' + rule, res.data)
                    sessionStorage.setItem('rank_page', 0)
                    $('.info').html('')
                    get_blog_infos()
                }
            }
        })
    },


//底部加载
    $(window).scroll(function () {
        var scrollerh = $(document).scrollTop();
        var viewbody = $(window).height();
        var allbody = $(document).height();
        //判断位置
        if (scrollerh + viewbody > allbody - 200) {
            count = $('.info>li').size()
            blog_ids = JSON.parse(sessionStorage.getItem('blog_ids'))
            page = parseInt(sessionStorage.getItem('page'))
            if (page + 10 < blog_ids.length) {
                //小于数组长度
                blog_ids = blog_ids.slice(page, page + 10)
                get_blog_info(blog_ids)
            } else if (blog_ids.length === page + 10) {
                //等于数组长度
                blog_ids = blog_ids.slice(page, blog_ids.length - 1)
                get_blog_info(blog_ids)
            } else {
                //大于数组长度
                //TODO 此处应有一个不同的底部提示
                $('.null').addClass('no_search_results')
            }
        }
    }),

    //小火箭
    $('.rocket-con').mouseover(function () {
        $('.rocket-con').addClass('fly')
    }).mouseout(function () {
        $('.rocket-con').removeClass('fly')
    }).on('click', function () {
        scrollTo(0, 0);
    }),
)