"""
Task 1 — Thu thập văn bản pháp luật về ma tuý và các chất cấm.

Tải tối thiểu 3 văn bản pháp luật (PDF) từ internet, lưu vào data/landing/legal/.
Nếu không có mạng, tự tạo PDF từ nội dung luật có sẵn.
"""
import subprocess
import sys
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

SOURCES = [
    {
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2022/01/73luat.pdf",
        "filename": "luat-phong-chong-ma-tuy-2021.pdf",
        "name": "Luật Phòng, chống ma túy 2021 (73/2021/QH14)",
    },
    {
        "url": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2021/12/105.signed_02.pdf",
        "filename": "nghi-dinh-105-2021.pdf",
        "name": "Nghị định 105/2021/NĐ-CP",
    },
    {
        "url": "https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2022/8/37734/41623-1-2022709-71057-2022-nd-cp.pdf",
        "filename": "nghi-dinh-57-2022-danh-muc-ma-tuy.pdf",
        "name": "Nghị định 57/2022/NĐ-CP (danh mục chất ma túy)",
    },
]


def _download(url: str, dest: Path) -> bool:
    """Tải file từ URL, trả về True nếu thành công."""
    try:
        result = subprocess.run(
            ["curl", "-sL", "--connect-timeout", "15", "--max-time", "60",
             "-o", str(dest), "-w", "%{http_code}|%{size_download}", url],
            capture_output=True, text=True, timeout=90,
        )
        stdout = result.stdout.strip()
        if "|" not in stdout:
            return False
        code_str, size_str = stdout.split("|", 1)
        if int(code_str) == 200 and int(size_str) > 5000:
            return True
    except Exception:
        pass

    if dest.exists():
        dest.unlink()
    return False


def _generate_pdf(filename: str, title: str, content: str):
    """Tạo PDF từ nội dung có sẵn (fallback khi không có mạng)."""
    from fpdf import FPDF
    font = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
    font_b = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("F", "", font)
    pdf.add_font("F", "B", font_b)
    pdf.set_font("F", "B", 13)
    pdf.multi_cell(0, 7, title, align="C")
    pdf.ln(4)
    pdf.set_font("F", "", 9)
    for para in content.split("\n\n"):
        para = para.strip()
        if para:
            pdf.multi_cell(0, 4.5, para)
            pdf.ln(1)
    path = DATA_DIR / filename
    pdf.output(str(path))


def collect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0

    for doc in SOURCES:
        dest = DATA_DIR / doc["filename"]
        print(f"  {doc['name']}")
        if _download(doc["url"], dest):
            size_kb = dest.stat().st_size / 1024
            print(f"    [DOWNLOADED] {size_kb:.0f} KB")
            downloaded += 1
        else:
            print(f"    Download failed — generating from content...")
            _generate_pdf(doc["filename"], doc["name"], _get_content(doc["filename"]))
            print(f"    [GENERATED] {doc['filename']}")

    print(f"\nDone: {downloaded}/{len(SOURCES)} downloaded, rest generated locally.")
    return True


def _get_content(filename: str) -> str:
    if "luat-phong-chong" in filename:
        return _LAW_CONTENT
    elif "nghi-dinh-105" in filename:
        return _ND105_CONTENT
    else:
        return _ND57_CONTENT


_LAW_CONTENT = """LUẬT PHÒNG, CHỐNG MA TÚY - Số: 73/2021/QH14

Chương I: NHỮNG QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Luật này quy định về phòng, chống ma túy; quản lý người sử dụng trái phép chất ma túy; cai nghiện ma túy; trách nhiệm của cá nhân, gia đình, cơ quan, tổ chức trong phòng, chống ma túy; quản lý nhà nước và hợp tác quốc tế về phòng, chống ma túy.

Điều 2. Giải thích từ ngữ
1. Chất ma túy là chất gây nghiện, chất hướng thần được quy định trong danh mục chất ma túy do Chính phủ ban hành.
2. Chất gây nghiện là chất kích thích hoặc ức chế thần kinh, dễ gây tình trạng nghiện đối với người sử dụng.
3. Chất hướng thần là chất kích thích hoặc ức chế thần kinh hoặc gây ảo giác, nếu sử dụng nhiều lần có thể dẫn tới tình trạng nghiện.
4. Tiền chất là hóa chất không thể thiếu được trong quá trình điều chế, sản xuất chất ma túy.
5. Cây có chứa chất ma túy là cây thuốc phiện, cây côca, cây cần sa và các loại cây khác có chứa chất ma túy do Chính phủ quy định.
6. Phòng, chống ma túy là phòng ngừa, ngăn chặn, đấu tranh chống tội phạm và tệ nạn ma túy; kiểm soát các hoạt động hợp pháp liên quan đến ma túy.
7. Người sử dụng trái phép chất ma túy là người có hành vi sử dụng chất ma túy mà không được sự cho phép của người hoặc cơ quan chuyên môn có thẩm quyền và xét nghiệm chất ma túy trong cơ thể có kết quả dương tính.
8. Người nghiện ma túy là người sử dụng chất ma túy, thuốc gây nghiện, thuốc hướng thần và bị lệ thuộc vào các chất này.
9. Cai nghiện ma túy là quá trình thực hiện các hoạt động hỗ trợ về y tế, tâm lý, xã hội, giúp người nghiện ma túy dừng sử dụng chất ma túy, phục hồi thể chất, tinh thần.

Điều 3. Chính sách của Nhà nước
1. Thực hiện đồng bộ các biện pháp phòng, chống ma túy; kết hợp với phòng, chống HIV/AIDS và các tệ nạn xã hội khác.
2. Tăng cường hoạt động tuyên truyền, giáo dục về công tác phòng, chống ma túy.
3. Ưu tiên nguồn lực phòng, chống ma túy cho vùng đồng bào dân tộc thiểu số và miền núi, vùng sâu, vùng xa, hải đảo, khu vực biên giới.
4. Bảo vệ, hỗ trợ cá nhân, gia đình, cơ quan, tổ chức tham gia phòng, chống ma túy.
5. Quản lý chặt chẽ người sử dụng trái phép chất ma túy; khuyến khích người nghiện ma túy tự nguyện cai nghiện.

Điều 4. Nguồn tài chính
1. Ngân sách nhà nước.
2. Nguồn tài trợ, viện trợ, đầu tư, tặng cho của tổ chức, cá nhân trong nước và ngoài nước.
3. Chi trả của gia đình, người nghiện ma túy.

Điều 5. Các hành vi bị nghiêm cấm
1. Trồng cây có chứa chất ma túy, hướng dẫn trồng cây có chứa chất ma túy.
2. Sản xuất, tàng trữ, vận chuyển, mua bán trái phép chất ma túy, tiền chất.
3. Sử dụng, tổ chức sử dụng trái phép chất ma túy; cưỡng bức, lôi kéo người khác sử dụng trái phép chất ma túy.
4. Chống lại hoặc cản trở việc xét nghiệm chất ma túy trong cơ thể, cai nghiện ma túy.
5. Kỳ thị người sử dụng trái phép chất ma túy, người cai nghiện ma túy.

Chương II: TRÁCH NHIỆM PHÒNG, CHỐNG MA TÚY

Điều 6. Trách nhiệm của cá nhân, gia đình
1. Tuyên truyền, giáo dục thành viên trong gia đình về tác hại của ma túy.
2. Thực hiện đúng chỉ định về sử dụng thuốc gây nghiện, thuốc hướng thần.
3. Hợp tác với cơ quan chức năng trong đấu tranh với tội phạm và tệ nạn ma túy.
4. Cung cấp kịp thời thông tin về tội phạm, tệ nạn ma túy cho cơ quan công an.

Điều 11. Cơ quan chuyên trách phòng, chống tội phạm về ma túy
1. Cơ quan chuyên trách bao gồm:
a) Cơ quan chuyên trách thuộc Công an nhân dân;
b) Cơ quan chuyên trách thuộc Bộ đội Biên phòng, Cảnh sát biển Việt Nam và Hải quan.
2. Cơ quan chuyên trách thuộc Công an nhân dân chủ trì, phối hợp thực hiện các hoạt động phòng ngừa, ngăn chặn và đấu tranh chống tội phạm về ma túy trên phạm vi toàn quốc.

Chương III: KIỂM SOÁT HOẠT ĐỘNG HỢP PHÁP

Điều 12. Các hoạt động hợp pháp liên quan đến ma túy bao gồm: nghiên cứu, giám định, sản xuất, vận chuyển, mua bán, xuất nhập khẩu chất ma túy, tiền chất được cơ quan có thẩm quyền cho phép.

---
Luật này được Quốc hội nước CHXHCN Việt Nam khóa XIV thông qua ngày 30/03/2021.
CHỦ TỊCH QUỐC HỘI: Nguyễn Thị Kim Ngân"""

_ND105_CONTENT = """NGHỊ ĐỊNH 105/2021/NĐ-CP
Quy định chi tiết và hướng dẫn thi hành một số điều của Luật Phòng, chống ma túy

Chương I: QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Nghị định này quy định chi tiết về công tác phối hợp của các cơ quan chuyên trách phòng, chống tội phạm về ma túy; kiểm soát các hoạt động hợp pháp liên quan đến ma túy và quản lý người sử dụng trái phép chất ma túy.

Điều 3. Nguyên tắc thực hiện
1. Công tác phối hợp phải tuân thủ pháp luật, bảo đảm sự đoàn kết, hiệp đồng, hỗ trợ lẫn nhau trên cơ sở chức năng, nhiệm vụ của từng bộ, ngành, địa phương.
2. Mỗi khu vực, địa bàn do một cơ quan chịu trách nhiệm chính, chủ trì. Lực lượng Công an nhân dân đóng vai trò nòng cốt trên phạm vi toàn quốc.
3. Kiểm soát các hoạt động hợp pháp liên quan đến ma túy phải được thực hiện chặt chẽ theo từng ngành, lĩnh vực, địa phương.
4. Quản lý người sử dụng trái phép chất ma túy phải bảo đảm tính công khai, khách quan, tôn trọng quyền và lợi ích hợp pháp của người bị quản lý.

Chương II: PHỐI HỢP CỦA CÁC CƠ QUAN CHUYÊN TRÁCH

Điều 4. Các lực lượng chuyên trách bao gồm:
a) Lực lượng Cảnh sát điều tra tội phạm về ma túy thuộc Công an nhân dân;
b) Lực lượng Phòng, chống ma túy và tội phạm thuộc Bộ đội Biên phòng;
c) Lực lượng chuyên trách thuộc Cảnh sát biển Việt Nam;
d) Lực lượng kiểm soát chống buôn lậu ma túy thuộc Hải quan.

Điều 5. Nội dung phối hợp:
1. Tham mưu, đề xuất xây dựng, sửa đổi cơ chế, chính sách, pháp luật về phòng, chống ma túy.
2. Tổ chức tuyên truyền, phổ biến, giáo dục pháp luật về phòng, chống ma túy.
3. Trao đổi thông tin về tình hình tội phạm, phương thức, thủ đoạn hoạt động, các loại ma túy mới.
4. Phối hợp thực hiện các biện pháp nghiệp vụ trinh sát, điều tra, xác minh, bắt giữ, xử lý.

Chương III: KIỂM SOÁT HOẠT ĐỘNG HỢP PHÁP

Điều 7. Thẩm quyền cấp phép:
1. Bộ Công an cấp phép nghiên cứu, sản xuất, vận chuyển chất ma túy và tiền chất.
2. Bộ Nông nghiệp và Phát triển nông thôn cấp phép hoạt động liên quan đến thuốc thú y.
3. Sở Công Thương cấp tỉnh cấp phép sản xuất tiền chất công nghiệp.

Điều 8. Kiểm soát hoạt động nghiên cứu, sản xuất, vận chuyển:
1. Nghiên cứu: thời hạn cấp phép 05 ngày làm việc.
2. Sản xuất: thời hạn cấp giấy chứng nhận đủ điều kiện là 30 ngày làm việc.
3. Vận chuyển: giấy phép có thời hạn không quá 06 tháng.

Chương IV: QUẢN LÝ NGƯỜI SỬ DỤNG TRÁI PHÉP CHẤT MA TÚY

Điều 12. Đối tượng bị quản lý: Người có hành vi sử dụng trái phép chất ma túy nhưng không thuộc trường hợp bị áp dụng biện pháp xử lý hành chính đưa vào cơ sở cai nghiện bắt buộc.

Điều 13. Căn cứ xét nghiệm chất ma túy trong cơ thể:
1. Tin báo, tố giác đã được xác minh.
2. Thông tin từ vụ vi phạm pháp luật.
3. Người có biểu hiện mất năng lực nhận thức nghi do ma túy.
4. Có dấu vết ma túy hoặc dụng cụ sử dụng trên người, phương tiện, nơi ở.

Điều 14. Quy trình lập hồ sơ và xác minh cư trú:
1. Cơ quan Công an nơi phát hiện hành vi tiến hành xác minh nơi cư trú trong vòng 03 ngày làm việc.
2. Nếu đối tượng có nơi cư trú ổn định, chuyển thông báo cho UBND cấp xã để quản lý.

Điều 15. Quyết định quản lý:
1. Chủ tịch UBND cấp xã ra Quyết định quản lý trong thời hạn 03 ngày làm việc.
2. Thành lập Tổ quản lý gồm: cán bộ Công an cấp xã (Tổ trưởng), đại diện thôn/tổ dân phố, đại diện gia đình, người uy tín.

Điều 16. Thời hạn quản lý là 01 năm. Nội dung quản lý bao gồm: xét nghiệm đột xuất, tư vấn tâm lý, giáo dục pháp luật, động viên tham gia hoạt động cộng đồng.

Chương V: ĐIỀU KHOẢN THI HÀNH
Nghị định này có hiệu lực thi hành kể từ ngày 01/01/2022.
TM. CHÍNH PHỦ - THỦ TƯỚNG: Phạm Minh Chính"""

_ND57_CONTENT = """NGHỊ ĐỊNH 57/2022/NĐ-CP
Quy định các danh mục chất ma túy và tiền chất

Điều 1. Danh mục các chất ma túy và tiền chất
Ban hành kèm theo Nghị định này Phụ lục các danh mục chất ma túy và tiền chất sau đây:

Danh mục I: Các chất ma túy tuyệt đối cấm sử dụng trong y học và đời sống xã hội; việc sử dụng các chất này trong nghiên cứu, kiểm nghiệm, giám định, điều tra tội phạm theo quy định đặc biệt của cơ quan có thẩm quyền.

Danh mục II: Các chất ma túy được sử dụng hạn chế trong nghiên cứu, kiểm nghiệm, giám định, điều tra tội phạm hoặc trong lĩnh vực y tế theo quy định của cơ quan có thẩm quyền.

Danh mục III: Các chất ma túy được sử dụng trong nghiên cứu, kiểm nghiệm, giám định, điều tra tội phạm hoặc trong lĩnh vực y tế, thú y theo quy định của cơ quan có thẩm quyền.

Danh mục IV: Các tiền chất (IVA: Các tiền chất thiết yếu, tham gia vào cấu trúc chất ma túy; IVB: Các tiền chất là hóa chất, dung môi, chất xúc tác dùng trong quá trình sản xuất chất ma túy).

Trong đó bổ sung 03 tiền chất ma túy vào Danh mục IV A:
- 1-boc-4-AP (tert-Butyl 4-(phenylamino) piperidine-1-carboxylate)
- 4-AP (N-Phenyl-4-piperidinamine)
- Norfentanyl (N-phenyl-N-4-piperidinyl-propanamide)

Như vậy, Danh mục IV A sẽ bao gồm 42 tiền chất thiết yếu. Danh mục IVB gồm 18 tiền chất là hóa chất, dung môi, chất xúc tác.

Điều 2. Trách nhiệm thực hiện
Các Bộ, cơ quan ngang Bộ, cơ quan thuộc Chính phủ, Ủy ban nhân dân các tỉnh, thành phố trực thuộc trung ương có trách nhiệm thực hiện Nghị định này.

Điều 3. Hiệu lực thi hành
Nghị định này có hiệu lực thi hành kể từ ngày 25 tháng 8 năm 2022.
Nghị định này thay thế Nghị định 73/2018/NĐ-CP và Nghị định 60/2020/NĐ-CP.

TM. CHÍNH PHỦ - KT. THỦ TƯỚNG - PHÓ THỦ TƯỚNG: Vũ Đức Đam"""


if __name__ == "__main__":
    ok = collect()
    sys.exit(0 if ok else 1)
