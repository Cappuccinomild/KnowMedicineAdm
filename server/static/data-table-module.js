import TagEditor from './cropper-tag.js';

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
            row.addEventListener('click', (event) => super.handleRowClick(event));
            tableElement.appendChild(row);
        });
    }

    isScrollAtBottom(containerElement) {
        return (
            containerElement.scrollTop + containerElement.clientHeight >=
            containerElement.scrollHeight
        );
    }

    initializeDataTable(apiUrl, tableContainerId, dataTableId, keyword) {
        const tableContainer = document.getElementById(tableContainerId);
        const dataTable = document.getElementById(dataTableId);
        this.keyword = keyword;
        
        // 테이블별 페이지 관리
        this.page[tableContainerId] = 1;

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

    async scrollEvent(apiUrl, tableContainerId, tableContainer, dataTable){
        if (!this.isLoading && this.isScrollAtBottom(tableContainer)) {
            this.isLoading = true;
            
            // 테이블별 페이지 관리
            this.page[tableContainerId] += 1;
            const queryPage = this.page[tableContainerId];

            
            console.log(apiUrl + queryPage);
            
            const newData = await this.fetchData(apiUrl + queryPage + "/" + this.keyword);
            this.appendDataToTable(newData.data, dataTable);
            this.isLoading = false;
        }
    }
}

// Export an instance of the class
export default DataTableModule;