#photoGallery
photo gallery read photos from dirs directly, it will show randomly little photos once.

## install
```bash
pip install -r requirements.txt
```

## how to run
you should config you photo dir in `config.py`.
```python
BASE_PHOTO_DIR = '/Users/galaio/testphoto/'
BASE_UPLOAD_DIR = '/Users/galaio/testphoto/upload/'
# 随机返回照片的数量
RANDOM_COUNT = 5
```

- with ngnix

you can config ngnix for photo server. add config to `/etc/ngnix/site-enable/default`.
```conf
server {
    ...
    location /photo {
        root /Users/galaio/testphoto;
        autoindex on;
        autoindex_exact_size on;
        autoindex_localtime on;
    }
}
```

- run server

```bash
python manager.py
```
server run default 8070 port.

