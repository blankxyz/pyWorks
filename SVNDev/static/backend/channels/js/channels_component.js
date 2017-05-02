Vue.component('paginator', {
    props: ['current', 'total','goto'],
    template: '<div class="box-footer with-border style="border-color: #1b6d85;height:62px">' +
    '<ul class="pagination pagination-bg" style="margin-top:5px">' +
        '<li v-bind:class="current != 1 ? \'active\' : \'disabled\'">' +
            '<a v-on:click="gotoPage(\'first\')"> 首页</a>' +
        '</li>' +
        '<li v-bind:class="1 < current ? \'active\' : \'disabled\'">' +
            '<a v-on:click="gotoPage(\'prev\')"> 上一页</a>' +
        '</li>' +
        '<li class="disabled">' +
            '<span>第 [[ current ]] 页</span><span> 共 [[ total ]] 页</span>' +
        '</li>' +
        '<li v-bind:class="current < total ? \'active\' : \'disabled\'">' +
            '<a v-on:click="gotoPage(\'next\')"> 下一页</a>' +
        '</li>' +
        '<li v-bind:class="current != total ? \'active\' : \'disabled\'">' +
            '<a v-on:click="gotoPage(\'last\')"> 末页</a>' +
        '</li>' +
        '<li>' +
        '<div class="col-md-1">' +
            '<div class="form-group">' +
                '<div class="input-group">' +
                    '<input v-model="goto" type="text" placeholder="  跳转页" value="[[goto]]" style="height:30px;width:60px">' +
                    '<div class="input-group-addon">' +
                        '<a v-on:click="gotoPage(\'goto\')">' +
                            '<i class="glyphicon glyphicon-play"></i>' +
                        '</a>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
        '</li>' +
    '</ul>' +
    '</div>',
    methods: {
        gotoPage: function (action) {
            console.log("action ",action, typeof(action));
            switch (action) {
                case "first":
                    this.current = 1;
                    break;
                case "last":
                    this.current = this.total;
                    break;
                case "next":
                    this.current++;
                    break;
                case "prev":
                    this.current--;
                    break;
                default: // "goto"
                    this.current = this.goto;
            }
            this.goto = this.current;
        }
    }
});