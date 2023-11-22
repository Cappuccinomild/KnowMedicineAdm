class TagEditor {
    constructor(fetchLink, saveLink) {
        this.fetchLink = fetchLink;
        this.saveLink = saveLink;
        this.tagList = [];
        this.imgSize;
        
        this.buttonBox = document.getElementById('btn_layer');
        this.nameArea = document.getElementById('ClassNameList');
        this.imgArea = document.getElementById('img');
        
        this.modifyMode = false;
        console.log(this.modifyMode);
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
                console.log(this.modifyMode);
            }.bind(this),
            ready: this.cropperReady.bind(this),
        });


        const rows = document.querySelectorAll('tr[data-imgId]');
        rows.forEach(row => {
            row.addEventListener('click', this.handleRowClick.bind(this));
        });

        const modifyButton = document.getElementById('modify');
        modifyButton.addEventListener('click', this.modifyToggle.bind(this));

        const addButton = document.getElementById('addTag');
        addButton.addEventListener('click', this.addTag.bind(this));

        const saveButton = document.getElementById('save');
        saveButton.addEventListener('click', this.saveChanges.bind(this));

        const nameInput = document.getElementById('ClassNameList');
        nameInput.addEventListener('input', this.handleNameInputChange.bind(this));

        const delButton = document.getElementById('delete');
        delButton.addEventListener('click', this.delTag.bind(this));
    }

    handleRowClick(event) {
        const imgId = event.currentTarget.getAttribute('data-imgId');

        fetch(`${this.fetchLink}${imgId}`)
            .then(response => response.json())
            .then(data => {
                if ('error' in data) {
                    console.error(data.error);
                } else {
                    if (this.modifyMode) {
                        this.modifyToggle();
                    }
                    this.cropper.replace(data.path);
                    this.buttonBox.innerHTML = '';
                    this.tagList = data;
                    for (let i = 0; i < this.tagList.data.length; i++) {
                        const label = document.createElement('label');
                        label.classList.add('btn', 'btn-outline-secondary');
                        label.id = this.tagList.data[i].tag_id;
                        label.textContent = `TAG ${i}`;
                        label.addEventListener('click', this.tagClick.bind(this, label, i));
                        this.buttonBox.appendChild(label);
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

    modifyToggle() {
        const modifyButton = document.getElementById('modify');
        if (this.modifyMode) {
            modifyButton.classList.remove('btn-success');
            modifyButton.classList.add('btn-outline-success');
        } else {
            modifyButton.classList.remove('btn-outline-success');
            modifyButton.classList.add('btn-success');
        }
        this.modifyMode = !this.modifyMode;
    }

    tagClick(label, index) {
        this.btnIndex = index;
        const tag = this.tagList.data[index];
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

        this.activeClear();

        if (label) {
            label.classList.add('active');
        }
    }

    activeClear() {
        const activeLabels = document.querySelectorAll('.btn-group-toggle .active');
        activeLabels.forEach(activeLabel => {
            activeLabel.classList.remove('active');
        });

        return activeLabels;
    }

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
        this.activeClear();
        label.classList.add('btn', 'btn-outline-secondary', 'active');
        label.id = tag.tag_id;
        const index = this.buttonBox.querySelectorAll('*').length;
        label.textContent = `TAG ${index}`;
        this.nameArea.value = tag.class_id;
        label.addEventListener('click', this.tagClick.bind(this, label, index));
        this.buttonBox.appendChild(label);
        this.tagList.data.push(tag);
        this.tagClick(label, index);
        console.log(tag);
    }

    handleNameInputChange() {
        const selectedOption = Array.from(document.getElementById('medicine_list_all').querySelectorAll('option'))
            .find(option => option.value === this.nameArea.value);
        
        if (selectedOption && this.modifyMode) {
            this.tagList.data[this.btnIndex].class_id = selectedOption.getAttribute('class-id');
            this.tagList.data[this.btnIndex].name = selectedOption.value;
        }
    }

    saveChanges() {
        if (this.modifyMode) {
            this.modifyToggle();
        }
        console.log(this.saveLink);
        console.log(this.tag_list);

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

    delTag(){
        let indexToRemove = this.btnIndex;

        this.tagList.data = this.tagList.data.slice(0, indexToRemove).concat(this.tagList.data.slice(indexToRemove + 1));

        this.saveChanges();
    
        document.querySelector(`[data-imgid="${this.tagList.id}"]`).click();
    }
}

export default TagEditor;