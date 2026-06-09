# src/s2_booking/image_urls.py
"""
Quản lý ảnh mặc định theo category — gán vòng tròn.
Được dùng bởi fetch_places.py (lúc cào OSM) và services.py (lúc trả response).
"""

# ── Điền URL ảnh của bạn vào đây ─────────────────────────────────────────────
# Mỗi category nên có 3-5 URL.

CATEGORY_PHOTOS: dict[str, list[str]] = {
    "cafe": [
        "https://mia.vn/media/uploads/blog-du-lich/lung-chung-cafe-1749203400.jpg",   
        "https://mia.vn/media/uploads/blog-du-lich/tiem-ca-phe-hoang-hon-chieu-1749203406.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/nha-ben-rung-1-1749203399.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/phia-tay-co-mat-troi-1749203402.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/hidden-land-dalat-1-1750474779.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnP4PJhDT3_azEI3pVr430HjNH7dIDKTDkPw&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsjdmjuOWKxMTC6b7yPdO5ICW3wWw4IEShGQ&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxtCTJHHRwJMCWs-Sz0aYZkfCd43i1nrhjHg&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAcerkbped_cHBqwE2LucUtCXxqfBeSiC5yg&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjDnUulU5S9q6rUX_HcQ7LU0MdzBsUId03Fw&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxg7ltuR04AfFtpjH3O8vCh2tEawDszfH_Zw&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYapk-jtXu9zn7ONrjet7yZ43KJJQJ0VPgKA&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdnfCzIF6Qk1pysFPvimdxE4GMDGy2t6dqMQ&s",
    ],
    "restaurant": [
        "https://gcs.tripi.vn/public-tripi/tripi-feed/img/473844cge/dearmoon-314039.jpg",
        "https://img.tripi.vn/cdn-cgi/image/width=700,height=700/https://gcs.tripi.vn/public-tripi/tripi-feed/img/473844XuX/nha-go-wooden-house-313806.jpg",
        "https://img.tripi.vn/cdn-cgi/image/width=700,height=700/https://gcs.tripi.vn/public-tripi/tripi-feed/img/473844qkB/lau-buffet-rau-da-lat-lagim-314215.jpg",
        "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0a/88/33/6e/1st-space.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2nxLe6vqkssIi8o5-Tw5Ul3y7qOvG3rIG-A&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRa12-QRgI0RxouybAP06O0mwQm5nY1DwI3lg&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRB5yfcUDAFUUjWuzXb1b_2yyAXAjbOulF09Q&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQVQwJ8lVsUTMIcwjh8J-rj8iXVZR249VRAg&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQvQ05PY8KljxDQsuEOgFc7jmbCGPu3Zhr_ng&s",
    ],
    "homestay": [
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-tai-1707926632.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-la-maison-1707926607.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-dan-1707926607.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-truly-home-1707926944.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-cui-1707926607.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-in-the-pines-1707926607.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-nap-1764338248.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-lung-chung-house-1764338248.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-the-burrow-1764338249.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-da-lat-view-home-1764338249.jpg",
        "https://mia.vn/media/uploads/blog-du-lich/homestay-vuon-tung-da-lat-4-1764648387.jpg",
    ],
    "hotel": [
        "https://tiki.vn/blog/wp-content/uploads/2022/12/khach-san-da-lat.jpg",
        "https://tiki.vn/blog/wp-content/uploads/2022/12/khach-san-eco-green.jpeg",
        "https://tiki.vn/blog/wp-content/uploads/2022/12/khach-san-bon-mua-da-lat-1068x712.webp",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYo7vQnY3wCGq2NUODOLbZoRcSw2BGG1PlZg&s",
        "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0a/77/ab/e2/ky-hoa-hotel-da-lat.jpg?w=900&h=500&s=1",
        "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1c/c8/92/8f/dalat-paradise-hotel.jpg?w=1200&h=1200&s=1",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQaPGXtLhCLxdougMQQQXBTzJ187U9xlHl7rQ&s",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgSRDU_6OuIF9SXP4M6d4_CJc4iF26j2qHXQ&s",
    ],
    "camping": [
        "https://homepage.momocdn.net/blogscontents/momo-upload-api-210712013827-637616507075623963.jpeg",
        "https://homepage.momocdn.net/blogscontents/momo-upload-api-210712013827-637616507076028823.jpeg",
        "https://dalatravel.vn/wp-content/uploads/2021/07/cam-trai-tai-da-lat-1.jpg",
        "https://bizweb.dktcdn.net/100/032/885/files/cam-trai-da-lat-voi-12-dia-diem-sau.jpg?v=1664854228123",
        "https://bizweb.dktcdn.net/100/032/885/files/mot-ngay-o-trong-rung.jpg?v=1667467790474",
        "https://bizweb.dktcdn.net/100/032/885/files/cam-trai-da-lat-tai-doi-da-phu-co-khung-canh-hung-vi.jpg?v=1664854391920"
    ],
}



def get_photo_by_index(category: str, index: int) -> str:
    
    pool = CATEGORY_PHOTOS.get(category, CATEGORY_PHOTOS["cafe"])
    return pool[index % len(pool)]


def get_photo_by_place_id(category: str, place_id: str) -> str:
    
    try:
        idx = int(place_id.replace("pl", ""))
    except ValueError:
        idx = abs(hash(place_id))
    return get_photo_by_index(category, idx)