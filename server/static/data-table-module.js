import TagEditor from './cropper-tag.js';
// 스크롤을 끝까지 내리면 자동으로 다음 페이지의 정보를 불러오는 class

class DataTableModule extends TagEditor{
    constructor(fetchLink, saveLink) {
        super(fetchLink, saveLink);
        this.page = {};
        this.isLoading = false;

        this.keyword = "";
        this.tableContainer;
        this.dataTable;
    }

    async fetchData(apiUrl) {
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`Error fetching data. Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            this.isLoading=false;
            throw new Error(`Network error: ${error.message}`);
        }
    }

    // 받아온 데이터를 테이블에 추가
    appendDataToTable(data, tableElement) {
        console.log(tableElement);
        data.forEach((item) => {
            const row = document.createElement('tr');

            row.classList.add('text-center');
            row.setAttribute('data-imgId', item.img_id);
            row.innerHTML = `<td>
            <input train-yn="${item.train_yn}" class="form-check-input" type="checkbox" value="${item.img_id}" id="flexCheckDefault">
            </td>
            <td>
            ${item.img_id}
            </td>
            <td>
            ${item.train_cnt}
            </td>`;

            console.log(row);

            // 상위 클래스인 cropper-tag.js 의 클릭이벤트를 가져옴
            row.addEventListener('click', (event) => super.handleRowClick(event));
            tableElement.appendChild(row);
        });
    }

    // 끝까지 스크롤을 내렸는지 여부 확인
    isScrollAtBottom(containerElement) {
        return (
            containerElement.scrollTop + containerElement.clientHeight >=
            containerElement.scrollHeight
        );
    }

    // 테이블 초기화
    initializeDataTable(apiUrl, tableContainerId, dataTableId, keyword) {
        const tableContainer = document.getElementById(tableContainerId);
        const dataTable = document.getElementById(dataTableId);
        this.keyword = keyword;
        
        // 테이블별 페이지 관리
        this.page[tableContainerId] = 1;

        // 스크롤을 끝까지 내렸을 경우의 이벤트
        tableContainer.addEventListener('scroll', async () => { this.scrollEvent.bind(this, apiUrl, tableContainerId, tableContainer, dataTable)(); });

        // Adjust max-height
        const adjustMaxHeight = () => {
            const windowHeight = window.innerHeight;
            const newMaxHeight = windowHeight * 0.7; // 70%
            tableContainer.style.maxHeight = newMaxHeight + 'px';
        };
        // Call adjustMaxHeight on window resize
        window.addEventListener('resize', adjustMaxHeight);

        // Initial adjustment
        adjustMaxHeight();
    }

    // 스크롤 끝까지 내렸을때의 이벤트
    async scrollEvent(apiUrl, tableContainerId, tableContainer, dataTable){

        // 로딩중이 아니고 스크롤이 가장 아래일때
        if (!this.isLoading && this.isScrollAtBottom(tableContainer)) {
            // 로딩중
            this.isLoading = true;
            
            // 테이블별 페이지 관리
            this.page[tableContainerId] += 1;
            const queryPage = this.page[tableContainerId];

            // 새 데이터를 받아서 기존 테이블에 추가함
            const newData = await this.fetchData(apiUrl + queryPage + "/" + this.keyword);
            this.appendDataToTable(newData.data, dataTable);

            // 로딩 완료
            this.isLoading = false;
        }
    }
}

// Export an instance of the class
export default DataTableModule;