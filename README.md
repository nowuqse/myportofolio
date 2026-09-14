# Portofolio

Name : Cindy Olivia Chai

NPM : 2506615753

Class : PBP C

## Description

This project is a personal portfolio website containing information about me, from my background, skills, and experiences. The website serves as a way to introduce myself, and it will be continuously developed throughout the semester as part of my coursework for PBP :D

### Tools

- Python
- HTML5
- CSS3
- Django 

## Progress Logs

| Week | Progress |
|------|----------|
| 1 | Set up initial project structure, git repository, and installing Django |
| 2 | Added new section such as skills and experiences |
| 3 | |

## Jawaban Tugas

### Tugas 1

1. Pada Tutorial dan Tugas 1, saya menggunakan beberapa elemen semantik HTML5 seperti section untuk membagi website menjadi beberapa bagian, seperti Profile, Favorite Song, Skills, dan Experiences. Penggunaan section membantu membuat struktur web menjadi lebih terorganisir karena setiap bagian memiliki penamaan dan konten yang jelas. Selain itu, struktur ini juga membuat kode HTML lebih mudah dibaca dan memudahkan ketika ingin mengatur styling setiap bagian menggunakan CSS.

2. Tantangan ketika membuat website responsive adalah menyesuaikan layout dari desktop ke ukuran mobile. Pada tampilan desktop, beberapa elemen dapat ditampilkan berdampingan dalam 1 baris yang sama, sedangkan pada tampilan mobile ruang yang tersedia jauh lebih kecil sehingga layout tersebut tidak lagi sesuai. Untuk mengevaluasinya, saya menggunakan responsive/device mode pada browser dan melihat bagian mana yang terlihat sulit dibaca di tampilan mobile. Contohnya pada skills dan experiences card, pada layar desktop mereka dapat dibuat berdampingan, tetapi ketika dilihat dalam tampilan mobile, card menjadi distorted dan terlihat dipaksa memanjang ke bawah. Oleh karena itu, dalam versi mobile daripada menggunakan layout yang sama, card dibuat menjadi satu kolom dan menyesuaikan ukuran serta posisi elemen sehingga lebih rapi dan nyaman dilihat pada layar kecil.

3. Karena website saat ini masih berupa static website, informasi yang ditampilkan masih harus ditulis dan diubah secara langsung pada kode HTML. Hal ini membuat website kurang fleksibel apabila ingin menambahkan atau memperbarui informasi seperti pengalaman, skills, atau project secara berkala. Selain itu, interaksi yang dapat diberikan kepada pengguna juga masih terbatas. Pada iterasi berikutnya, saya ingin menambahkan lebih banyak fungsionalitas interaktif, salah satunya button play pada bagian musik ingin dibuat menyesuaikan kondisi apakah lagu sedang diputarkan atau tidak. Untuk pengembangan yang lebih lanjut, saya juga ingin membuat data seperti projects dan experiences dapat dikelola secara dinamis, sehingga informasi dapat diperbarui tanpa harus mengubah HTML secara langsung.

### Tugas 2
1. Alur yang terjadi ketika pengguna membuka halaman portofolio baru dimulai dari user request untuk membuka halaman tersebut. Request pertama kali diterima oleh `portofolio/urls.py` sebagai pintu utama yang mengarahkan ke aplikasi yang sesuai dari request tersebut. Misalnya, ketika user membuka `/admin/` maka akan diarahkan pada Django Admin. Sementara itu, untuk URL lainnya, akan diserahkan pengaturannya pada `main/urls.py`. Kemudian, `main/urls.py` akan mencocokkan sisa URL dengan route untuk halaman spesifiknya, misalnya:

```bash
path("project/", show_project, name="show_project")
```

Route tersebut mengarahkan request ke view show_project.

```bash
/                 → show_main
/experience/      → show_experience
/project/         → show_project
```

Setelah itu, `views.py` menentukan apa yang dilakukan ketika URL tersebut dipanggil. Misalnya, pada halaman project, `show_project` mengambil data project yang tersimpan di database melalui model Project yang didefinisikan di `models.py`. Data tersebut kemudian dikirim melalui context ke template, yaitu `project.html`. Selanjutnya, `project.html` akan melakukan loop terhadap data project dan menampilkannya sebagaimana data ingin ditampilkan. Jika belum ada data, template menampilkan kondisi kosong seperti `"No project added."` Setelah proses tersebut selesai, HTML yang dihasilkan dikirim kembali dan ditampilkan pada browser pengguna.

2. Data untuk bagian portofolio baru disimpan pada model agar data dan tampilan dapat dipisahkan. Model bertugas menyimpan dan mengelola data project di database, sedangkan template bertugas menampilkan data tersebut. Dengan begitu, jika ingin menambah, mengubah, atau menghapus project, kita tidak perlu mengubah kode HTML secara langsung, tetapi cukup mengubah data yang tersimpan pada database.

Hal ini membuat aplikasi lebih mudah di-maintenance dan dikembangkan. Misalnya pada tugas ini, jika jumlah project ataupun experience bertambah, template yang sama tetap dapat digunakan tanpa harus menambahkan HTML baru untuk setiap data baru yang ditambahkan. 

3. `makemigrations` digunakan untuk membuat file migration berdasarkan perubahan yang dilakukan pada `models.py`, sedangkan `migrate` digunakan untuk menerapkan perubahan tersebut ke database. Contohnya pada tugas ini, setelah menambahkan model `Project` yang memiliki field `title`, `description`, dan `category`, dijalankan 

```bash
python manage.py makemigrations 
python manage.py migrate
```

untuk membuat file migration baru dan menerapkan perubahan tersebut sehingga tabel `Project` dibuat di database.


## AI Disclosure

As a first-timer HTML and CSS, I used ChatGPT as a learning tool to understand the code and syntax given by the course. Rather than directly copying the generated code, I used ChatGPT to explain concepts that I did not understand and help me identify possible solutions. I then reviewed, tested, and modified the code manually to fit my taste :3 (website's design) and requirements. Well although ChatGPT was helpful, its suggestions were not always directly applicable to my existing code. Sometimes, the generated code suggested using JavaScript even though I had not learned JavaScript yet :/ Another limitation was that AI couldnt really provide a solution while fully understanding the visual result I wanted. For example, when working on the song card, I needed to test the website myself to determine whether the padding and margin fullfilled what i wanted.

Therefore, I used AI mainly as a learning and debugging assistant, rather than relying on it to build the website independently. 