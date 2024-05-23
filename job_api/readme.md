### Endpoint: Get Jobs

#### URL
```
GET /api/joblist/
```

#### Parameters

1. **jobName** (optional)
   - **Description:** Nama pekerjaan yang ingin dicari. Anda bisa menggunakan kata kunci dengan tanda minus (-) sebagai pengganti spasi.
   - **Type:** String
   - **Example:** `data-analyst`

2. **publicationDate** (optional)
   - **Description:** Tanggal publikasi pekerjaan. Format yang diharapkan adalah `YYYY-MM-DD`.
   - **Type:** String
   - **Example:** `2024-05-22`

3. **publicationDateAfter** (optional)
   - **Description:** Tanggal publikasi setelah (termasuk) tanggal yang diberikan. Format yang diharapkan adalah `YYYY-MM-DD`.
   - **Type:** String
   - **Example:** `2024-05-01`

4. **publicationDateBefore** (optional)
   - **Description:** Tanggal publikasi sebelum (termasuk) tanggal yang diberikan. Format yang diharapkan adalah `YYYY-MM-DD`.
   - **Type:** String
   - **Example:** `2024-05-15`

5. **publicationDateCategory** (optional)
   - **Description:** Kategori tanggal publikasi, seperti "today", "two_days_ago", "one_week_ago", "two_weeks_ago", atau "one_month_ago".
   - **Type:** String
   - **Example:** `today`

6. **jobLocation** (optional)
   - **Description:** Lokasi pekerjaan yang ingin dicari.
   - **Type:** String
   - **Example:** `Jakarta`

7. **company** (optional)
   - **Description:** Nama perusahaan yang ingin dicari.
   - **Type:** String
   - **Example:** `Tech Solutions`

8. **limit** (optional)
   - **Description:** Batas jumlah pekerjaan yang akan ditampilkan.
   - **Type:** Integer
   - **Example:** `10`

9. **page** (optional)
   - **Description:** Nomor halaman untuk pagination.
   - **Type:** Integer
   - **Example:** `1`

#### Example Request
```
GET http://127.0.0.1:8000/api/joblist/?jobName=data-analyst&publicationDateAfter=2024-05-01&publicationDateBefore=2024-05-15&jobLocation=Jakarta&company=Tech%20Solutions&limit=10&page=1
```

#### Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

##### Example Response
```json
{
    "total": 2,
    "results": [
        {
            "id": 1,
            "job_name": "Data Analyst",
            "publication_date": "2024-05-10",
            "job_location": "Jakarta, Indonesia",
            "company": "Tech Solutions",
            "source": "jobstreet.co.id",
            "source_url": "https://jobstreet.co.id/job/12345"
        },
        {
            "id": 2,
            "job_name": "Data Scientist",
            "publication_date": "2024-05-12",
            "job_location": "Jakarta, Indonesia",
            "company": "Data Corp",
            "source": "linkedin.com",
            "source_url": "https://linkedin.com/job/67890"
        }
    ]
}
```

#### Error Responses

- **Status Code:** 400 Bad Request
- **Content-Type:** application/json

##### Example Error Response (Invalid date format)
```json
{
    "error": "Invalid format for publicationDateAfter. Use YYYY-MM-DD."
}
```

### Notes

- Semua parameter bersifat opsional.
- Jika tidak ada parameter yang diberikan, semua pekerjaan yang ada di database akan ditampilkan.
- Parameter `jobName`, `jobLocation`, dan `company` menggunakan pencarian dengan metode `icontains`, sehingga hasil pencarian akan mencakup semua pekerjaan yang mengandung kata kunci yang diberikan.
- Parameter `publicationDateAfter` dan `publicationDateBefore` memerlukan format tanggal `YYYY-MM-DD`.
- Parameter `publicationDateCategory` memungkinkan pengguna untuk mencari pekerjaan berdasarkan kategori tanggal publikasi.

### How to Use

1. **Menampilkan semua pekerjaan:**
   ```
   GET http://127.0.0.1:8000/api/joblist/
   ```

2. **Menampilkan pekerjaan berdasarkan nama:**
   ```
   GET http://127.0.0.1:8000/api/joblist/?jobName=data-analyst
   ```

3. **Menampilkan pekerjaan berdasarkan tanggal publikasi setelah tanggal tertentu:**
   ```
   GET http://127.0.0.1:8000/api/joblist/?publicationDateAfter=2024-05-01
   ```

4. **Menampilkan pekerjaan berdasarkan lokasi:**
   ```
   GET http://127.0.0.1:8000/api/joblist/?jobLocation=Jakarta
   ```

5. **Menggunakan limit dan halaman untuk pagination:**
   ```
   GET http://127.0.0.1:8000/api/joblist/?limit=10&page=1
   ```