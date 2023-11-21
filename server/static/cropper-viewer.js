
    /* 약품 상세 정보(AJAX) */
    var tag_list;
    var btn_index = 0;
    var img_size;
    var modifyMode = false;
    const rows = document.querySelectorAll('tr[data-imgId]');
    const nameArea = document.getElementById('ClassNameList');
    const imgArea = document.getElementById('img');
    const usageTextarea = document.getElementById('usage');
    const cautionTextarea = document.getElementById('caution');
    const buttonBox = document.getElementById('btn_layer');
    const cropper = new Cropper(imgArea, 
    {
        viewMode: 1, // 크롭 박스가 이미지를 완전히 포함하도록 설정
        zoomable:false,
        rotatable:false,
        movable:false,
        toggleDragModeOnDblClick:false,
        crop(event) {
                
                if(modifyMode){
                    const cropBox = cropper.getCropBoxData();

                    tag_list.data[btn_index].width = cropBox.width / img_size.width;
                    tag_list.data[btn_index].height = cropBox.height / img_size.height;

                    tag_list.data[btn_index].left = cropBox.left / img_size.width + tag_list.data[btn_index].width / 2;
                    tag_list.data[btn_index].top = cropBox.top / img_size.height + tag_list.data[btn_index].height / 2;
                }
                else{
                    // alert("수정 모드가 활성화되어있지 않습니다.");
                }
        },
        ready() {
            // 로드되고 난 후의 작업
            // 첫 번째 태그를 불러옴
            img_size = this.cropper.getContainerData();

            tag = tag_list.data[0];

            const width = tag.width * img_size.width;
            const height = tag.height * img_size.height;

            const left = tag.left * img_size.width - width/2;
            const top = tag.top * img_size.height - height/2;

            cropper.setCropBoxData({
                'left' : left,
                'top' : top,
                'width' : width,
                'height' : height,
            });

            document.getElementById('ClassNameList').value = tag.class_id;
        },
    });

    function adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';

    }

    // select값 수정 이벤트
    function selectChange() {
        
        if(modifyMode){
            tag_list.data[btn_index].class_id = document.getElementById('ClassNameList').value;
        }
        
    }

    // 수정모드 설정
    function modifyToggle(element){

        if (modifyMode){
            element.classList.remove('btn-success');
            element.classList.add('btn-outline-success');
            modifyMode = false;
        }
        else{
            element.classList.remove('btn-outline-success');
            element.classList.add('btn-success');
            modifyMode = true;
        }

        console.log(modifyMode);

    }

    function tagClick(label, index) {
        
        return function() {
            btn_index = index;
            const tag = tag_list.data[index];

            // 태그 정보 cropper에 적용
            const width = tag.width * img_size.width;
            const height = tag.height * img_size.height;

            const left = tag.left * img_size.width - width/2;
            const top = tag.top * img_size.height - height/2;

            cropper.setCropBoxData({
                'left' : left,
                'top' : top,
                'width' : width,
                'height' : height,
            });

            // 약품 이름 설정
            nameArea.value = tag.class_id;

            // active 클래스 제거
            activeClear();

            // 현재 클릭한 label에 active 클래스 추가
            label.classList.add('active');
        };
    }

    function activeClear(){
        const activeLabels = document.querySelectorAll('.btn-group-toggle .active');

        activeLabels.forEach(activeLabel => {
        activeLabel.classList.remove('active');
        });
    }

    // 태그추가 버튼
    function add_tag(){

        const nowData = cropper.getCropBoxData();
        
        // 태그데이터 초기화
        const tag = {
            'tag_id':"",
            'name':document.getElementById("ClassNameList").options[document.getElementById("ClassNameList").selectedIndex].text,
            'class_id': document.getElementById("ClassNameList").value,
            'left': 0,
            'top': 0,
            'width': 0,
            'height': 0,
        };
        console.log(tag);
        const label = document.createElement('label');

        activeClear();
        label.classList.add('btn', 'btn-outline-secondary', 'active');
        
        label.id = tag.tag_id;

        // 전체 버튼의 개수
        const index = buttonBox.querySelectorAll('*').length;
        label.textContent = 'TAG ' + index;

        nameArea.value = tag.class_id;
        
        label.addEventListener('click', tagClick(label, index));
        
        
        buttonBox.appendChild(label);
        tag_list.data.push(tag);

        //추가 후 버튼 클릭 구현
        tagClick(label, index)();

    }
    rows.forEach(function (row) {
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
    });

    function modDataSubmit(){

        // 수정모드가 켜져있을 경우 해제
        if (modifyMode){
            modifyToggle(document.getElementById('modify'));
        }
        fetch(`/model/tag_save/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(
                tag_list
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
