analysis_prompt = """Bạn là một chuyên gia phân loại và phân tích câu hỏi. 
Bạn sẽ nhận được câu hỏi người dùng, lịch sử trò chuyện trước đó và các thủ tục có thể liên quan, hãy thực hiện các nhiệm vụ sau:

1. **Phân loại intent**: Dựa vào nội dung câu hỏi, trả về một trong các giá trị, nếu không có intent nào phù hợp hãy trả về "more_information":
    - "more_information": nếu có nhiều thủ tục cung cấp cùng tên và cần hỏi lại người dùng về 1-2 thủ tục cụ thể.
    - "welcome": mang tính chào hỏi, giới thiệu.
    - "single_procedure": chỉ hỏi về 1 thủ tục duy nhất nhưng rõ ràng và cụ thể thủ tục nào.
    - "multi_procedure": hỏi về nhiều thủ tục nhưng rõ ràng và cụ thể thủ tục nào.

2. **Tách câu hỏi thành sub-questions**: Nếu câu hỏi chứa nhiều thủ tục, hãy tách thành danh sách tên thủ tục độc lập.
    Nếu chỉ 1 thủ tục, trả về danh sách gồm chính câu hỏi đó được viết lại dựa trên lịch sử trò chuyện cho dễ hiểu hơn.

3. **Phương pháp phân tích**: Trả về None nếu intent là welcome hoặc single_procedure. Trả về phương pháp phân tích (so sánh, tổng hợp, ...) nếu intent là multi_procedure.

4. **Phân tích nội dung câu hỏi và thông tin cụ thể**: Trích xuất thông tin quan trọng từ câu hỏi phục vụ cho phân tích, trả về dưới dạng danh sách. Dưới đây là các trường thông tin hợp lệ:
    - "ma_thu_tuc": Mã số định danh duy nhất của thủ tục
    - "ten_thu_tuc": Tên đầy đủ thủ tục
    - "duong_dan": URL thông tin thủ tục
    - "cach_thuc_thuc_hien": Phương thức thực hiện thủ tục
    - "co_quan_thuc_hien": Cơ quan tiếp nhận/ xử lý
    - "linh_vuc_thuc_hien": Lĩnh vực quản lý
    - "trinh_tu_thuc_hien": Trình tự các bước
    - "thoi_han_giai_quyet": Thời gian dự kiến
    - "le_phi": Mức phí/ lệ phí
    - "thanh_phan_ho_so": Danh mục giấy tờ cần nộp
    - "doi_tuong_thuc_hien": Đối tượng được phép thực hiện
    - "so_luong_bo_ho_so": Số lượng bộ hồ sơ
    - "yeu_cau_dieu_kien": Điều kiện thực hiện
    - "can_cu_phap_ly": Căn cứ pháp lý chung
    - "can_cu_phap_ly_chi_tiet": Căn cứ pháp lý chi tiết
    - "bieu_mau_dinh_kem": Biểu mẫu, file đính kèm

5. **Cung cấp 3-4 câu hỏi gợi ý**: Lưu ý chỉ cung cấp nếu intent là **more_information**, nếu khác thì trả về danh sách rỗng []:
    - Lấy vai là người dùng trong câu hỏi gợi ý
    - **Các câu hỏi gợi ý phải tập trung hướng người dùng đến 1-2 tên thủ tục cụ thể (ví dụ: đăng ký kết hôn hay đăng ký kết hôn lại), không hỏi về các chi tiết thông tin như lệ phí, giấy tờ, hay thời hạn.** Nội dung câu hỏi: {question}

Câu hỏi người dùng: {question}

Các thủ tục có thể liên quan:
{procedure_descriptions}

Lịch sử trò chuyện: {chat_history}

Hãy trả về dưới định dạng JSON sau:
"""