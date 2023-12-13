class TagEditor {
    constructor(fetchLink, saveLink) {
        this.fetchLink = fetchLink;
        this.saveLink = saveLink;
        this.tagList = [];
        this.imgSize;
        this.selectedRow = null;
        
        this.buttonBox = document.getElementById('btn_layer');

        // 약품명을 출력하는 라벨에 기본 읽기모드 설정
        this.nameArea = document.getElementById('ClassNameList');
        this.nameArea.setAttribute("readonly", true);

        this.imgArea = document.getElementById('img');
        
        this.modifyMode = false;
        this.btnIndex = 0;

        this.cropper = new Cropper(this.imgArea, {
            viewMode: 1,
            zoomable: false,
            rotatable: false,
            movable: false,
            toggleDragModeOnDblClick: false,
            crop: function (event) {
                if (this.modifyMode) {
                    const cropBox = this.cropper.getCropBoxData();
                    console.log(this.tagList.data);
                    this.tagList.data[this.btnIndex].width = cropBox.width / this.imgSize.width;
                    this.tagList.data[this.btnIndex].height = cropBox.height / this.imgSize.height;
                    this.tagList.data[this.btnIndex].left = cropBox.left / this.imgSize.width + this.tagList.data[this.btnIndex].width / 2;
                    this.tagList.data[this.btnIndex].top = cropBox.top / this.imgSize.height + this.tagList.data[this.btnIndex].height / 2;
                }
            }.bind(this),
            ready: this.cropperReady.bind(this),
        });

        // 테이블 내부의 요소에 클릭이벤트 추가
        // img id 기준으로 세부 내용을 가져오도록 한다
        const rows = document.querySelectorAll('tr[data-imgId]');
        rows.forEach(row => {
            row.addEventListener('click', this.handleRowClick.bind(this));
        });

        // 수정 버튼 이벤트
        const modifyButton = document.getElementById('modify');
        if (modifyButton){
        modifyButton.addEventListener('click', this.modifyToggle.bind(this));
        }

        // 태그 추가 버튼 이벤트
        const addButton = document.getElementById('addTag');
        if (addButton){
            addButton.addEventListener('click', this.addTag.bind(this));
        }
        
        // 저장 버튼 이벤트
        const saveButton = document.getElementById('save');
        if (saveButton){
            saveButton.addEventListener('click', this.saveChanges.bind(this));
        }

        // 상단 약품 명 변경 이벤트
        const nameInput = document.getElementById('ClassNameList');
        if (nameInput){
            nameInput.addEventListener('input', this.handleNameInputChange.bind(this));
        }

        // 태그 삭제 이벤트
        const delButton = document.getElementById('delete');
        if (modifyButton){
            delButton.addEventListener('click', this.delTag.bind(this));
        }
    }

    getFechLink(){
        return this.fetchLink;
    }

    handleRowClick(event) {
        const imgId = event.currentTarget.getAttribute('data-imgId');

        // 기존 클릭한 행에 대한 클래스 제거
        if (this.selectedRow) {
            this.selectedRow.classList.remove('table-active');
        }

        // 현재 클릭한 행에 대한 클래스 추가
        this.selectedRow = event.currentTarget;
        this.selectedRow.classList.add('table-active');
        
        fetch(`${this.fetchLink}${imgId}`)
            .then(response => response.json())
            .then(data => {
                if ('error' in data) {
                    console.error(data.error);
                } else {
                    // 수정 모드일 경우 수정 모드를 해제함
                    if (this.modifyMode) {
                        this.modifyToggle();
                    }

                    // 배경 이미지 변경
                    this.cropper.replace(data.path);

                    // 태그 버튼박스 초기화
                    this.buttonBox.innerHTML = '';

                    // 태그 정보 초기화
                    this.tagList = data;

                    // 태그 별 버튼 추가
                    for (let i = 0; i < this.tagList.data.length; i++) {
                        const label = document.createElement('label');

                        // 태그 버튼 추가
                        label.classList.add('btn', 'btn-outline-secondary');
                        label.id = this.tagList.data[i].tag_id;
                        label.textContent = `TAG ${i}`;

                        // 태그 클릭 이벤트 추가
                        label.addEventListener('click', this.tagClick.bind(this, label, i));
                        this.buttonBox.appendChild(label);
                        
                        // 첫번째 태그 클릭 이벤트
                        if (i === 0) {
                            label.classList.add('active');
                            this.tagClick(label, 0);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('약품 정보를 가져오는 중 오류 발생:', error);
            });
    }

    // cropper 박스 초기화
    cropperReady() {
        this.imgSize = this.cropper.getContainerData();
        const tag = this.tagList.data[0];
        const width = tag.width * this.imgSize.width;
        const height = tag.height * this.imgSize.height;
        const left = tag.left * this.imgSize.width - width / 2;
        const top = tag.top * this.imgSize.height - height / 2;

        this.cropper.setCropBoxData({
            'left': left,
            'top': top,
            'width': width,
            'height': height,
        });

        this.nameArea.value = tag.name;
    }

    // 수정 모드 on/off
    modifyToggle() {
        const modifyButton = document.getElementById('modify');
        
        if (this.modifyMode) {
            // 버튼 색 변경
            modifyButton.classList.remove('btn-success');
            modifyButton.classList.add('btn-outline-success');

            // 약품명 수정 가능 여부 변경
            this.nameArea.readOnly = true;
        } else {
            // 버튼 색 변경
            modifyButton.classList.remove('btn-outline-success');
            modifyButton.classList.add('btn-success');

            // 약품명 수정 가능 여부 변경
            this.nameArea.readOnly = false;
        }

        // 수정모드 on / off 토글
        this.modifyMode = !this.modifyMode;
    }

    // 태그버튼 클릭 이벤트
    tagClick(label, index) {
        this.btnIndex = index;

        // 픽셀 데이터를 비율 데이터로 변환한다
        const tag = this.tagList.data[index];
        const width = tag.width * this.imgSize.width;
        const height = tag.height * this.imgSize.height;
        const left = tag.left * this.imgSize.width - width / 2;
        const top = tag.top * this.imgSize.height - height / 2;

        // 변환한 데이터를 cropper에 업데이트
        this.cropper.setCropBoxData({
            'left': left,
            'top': top,
            'width': width,
            'height': height,
        });
        
        // 약품 명 업데이트
        this.nameArea.value = tag.name;

        // 클릭되어있는 버튼 초기화
        this.activeClear();

        // 클릭한 버튼 색깔 변화
        if (label) {
            label.classList.add('active');
        }
    }

    // box리스트에서 active 클래스를 없앤다
    activeClear() {
        const activeLabels = document.querySelectorAll('.btn-group-toggle .active');
        activeLabels.forEach(activeLabel => {
            activeLabel.classList.remove('active');
        });

        return activeLabels;
    }

    // 새로운 태그 추가
    addTag() {
        this.nameArea.value ="";
        const tag = {
            'tag_id': "",
            'name': "",
            'class_id': "",
            'left': 0,
            'top': 0,
            'width': 0,
            'height': 0,
        };
        const label = document.createElement('label');

        // active 초기화
        this.activeClear();

        // 클릭된 상태로 class 설정
        label.classList.add('btn', 'btn-outline-secondary', 'active');
        label.id = tag.tag_id;

        // 버튼박스의 맨 뒤에 추가한다
        const index = this.buttonBox.querySelectorAll('*').length;
        label.textContent = `TAG ${index}`;
        this.nameArea.value = tag.class_id;

        // 태그클릭 이벤트 추가
        label.addEventListener('click', this.tagClick.bind(this, label, index));

        // 버튼박스에 추가
        this.buttonBox.appendChild(label);

        // 태그 목록에 초기화된 데이터 추가
        this.tagList.data.push(tag);

        // 추가한 태그 정보를 클릭
        this.tagClick(label, index);
    }

    // 약품명 변경 이벤트 처리
    handleNameInputChange() {
        const selectedOption = Array.from(document.getElementById('medicine_list_all').querySelectorAll('option'))
            .find(option => option.value === this.nameArea.value);
        
        if (selectedOption && this.modifyMode) {
            this.tagList.data[this.btnIndex].class_id = selectedOption.getAttribute('class-id');
            this.tagList.data[this.btnIndex].name = selectedOption.value;
        }
    }

    // 수정한 정보 저장
    saveChanges() {

        // 수정 모드일 경우에 수정 이후 수정모드를 종료함
        if (this.modifyMode) {
            this.modifyToggle();
        }
        console.log(this.saveLink);
        console.log(this.tag_list);

        // tag_list 정보를 서버로 전달
        fetch(this.saveLink, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(
                this.tagList
            ),
        }).then((data) => {
            // 성공적으로 JSON 데이터를 받았을 때
            console.log(data); // 받은 데이터를 로그에 출력
            alert('성공적으로 저장되었습니다.');
        })
        .catch((error) => {
            // 오류가 발생했을 때
            console.error('오류 발생:', error);
            alert('저장에 실패했습니다. 다시 시도해주세요.');
        });
    }

    // 태그 정보 삭제
    delTag(){

        // 현재 선택되어있는 태그 정보를 삭제한다
        let indexToRemove = this.btnIndex;

        // tagList 정보 업데이트
        this.tagList.data = this.tagList.data.slice(0, indexToRemove).concat(this.tagList.data.slice(indexToRemove + 1));

        // save 요청 전송
        this.saveChanges();
        
        // 맨 첫번째 요소 클릭
        document.querySelector(`[data-imgid="${this.tagList.id}"]`).click();
    }
}

export default TagEditor;