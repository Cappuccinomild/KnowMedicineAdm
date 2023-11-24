class SearchKw {
    constructor(btn_id, input_id) {
        this.btn_id = btn_id;
        this.input_id = input_id;
    }

    initializeSearchKw(){
        const btn_search = document.getElementById(this.btn_id);
        btn_search.addEventListener('click', function () {
            document.getElementById('kw').value = document.getElementById('search_kw').value;
            document.getElementById('page').value = 1; // 검색 시 1페이지부터 조회
            document.getElementById('searchForm').submit();
        })

        const search_kw = document.getElementById(this.input_id);
        search_kw.addEventListener('keyup', function (event) {
            if (event.key === "Enter") {
                document.getElementById('kw').value = search_kw.value;
                document.getElementById('page').value = 1; // 검색 시 1페이지부터 조회
                document.getElementById('searchForm').submit();
            }
        });
    }
    
}

export default TagEditor;


    