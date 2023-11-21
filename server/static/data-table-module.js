class DataTableModule {
    constructor() {
        this.page = 1;
    }

    async fetchData(apiUrl) {
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`Error fetching data. Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            throw new Error(`Network error: ${error.message}`);
        }
    }

    appendDataToTable(data, tableElement) {
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

            row.addEventListener('click', function () {
                const imgId = this.getAttribute('data-imgId');
    
                fetch(`/model/data_detail/${imgId}`)
                    .then(response => response.json())
                    .then(data => {
                        if ('error' in data) {
                            console.error(data.error);
                        } else {
    
    
                            // 수정모드가 켜져있을 경우 해제
                            if (modifyMode){
                                modifyToggle(document.getElementById('modify'));
                            }
                            
                            cropper.replace(data.path);
                            
                            // 기존 버튼 제거
                            buttonBox.innerHTML='';
    
                            tag_list = data;
    
                            let i = 0;
                            for (const tag of tag_list.data){
                                const label = document.createElement('label');
    
                                label.classList.add('btn', 'btn-outline-secondary');
                                
                                label.id = tag.tag_id;
                                
                                label.textContent = 'TAG ' + i;
                                
                                label.addEventListener('click', tagClick(label, i));
                                // 버튼을 추가할 div에 버튼을 추가
                                buttonBox.appendChild(label);
                                if(i == 0){
                                    label.classList.add('active');
                                }
                                i++;
                            }
                        }
                    })
                    .catch(error => {
                        console.error('약품 정보를 가져오는 중 오류 발생:', error)
                    });
            });
            tableElement.appendChild(row);
        });
    }

    isScrollAtBottom(containerElement) {
        return (
            containerElement.scrollTop + containerElement.clientHeight >=
            containerElement.scrollHeight
        );
    }

    initializeDataTable(tableContainerId, dataTableId, apiUrl) {
        const tableContainer = document.getElementById(tableContainerId);
        const dataTable = document.getElementById(dataTableId);
        let isLoading = false;

        let match = apiUrl.match(/\/model\/data_q_list\/(\d+)\/Y\//);

        tableContainer.addEventListener('scroll', async () => {
            if (!isLoading && this.isScrollAtBottom(tableContainer)) {
                isLoading = true;
                this.page += 1;
                console.log(this.page);
                if (match) {
                    // 변경된 URL 생성
                    match = apiUrl.match(/\/model\/data_q_list\/(\d+)\/Y\//);
                    apiUrl = apiUrl.replace(match[1], this.page);
                    console.log(apiUrl);
                } else {
                    console.error('URL 형식이 일치하지 않습니다.');
                }

                const newData = await this.fetchData(apiUrl);
                this.appendDataToTable(newData.data, dataTable);
                isLoading = false;
            }
        });

        // Adjust max-height
        function adjustMaxHeight() {
            const windowHeight = window.innerHeight;
            const newMaxHeight = windowHeight * 0.7; // 70%
            tableContainer.style.maxHeight = newMaxHeight + 'px';
        }

        // Call adjustMaxHeight on window resize
        window.addEventListener('resize', adjustMaxHeight);

        // Initial adjustment
        adjustMaxHeight();
    }
}

// Export an instance of the class
export default DataTableModule;