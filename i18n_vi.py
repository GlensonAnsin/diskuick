"""Vietnamese strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("vi", "Tiếng Việt", (
    "Tổng quan", "Trò chơi", "Công cụ", "Cài đặt",                                                     # 1-5
    "Giữ ổ đĩa của bạn luôn thức khi bạn chơi",
    "Các lần khựng gần đây", "Sức khỏe ổ đĩa", "Kiểm tra lag", "Đo hiệu năng & tự động tinh chỉnh",
    "Hành vi", "Giao diện", "Khi nào chạy", "Cường độ mặc định",                                       # 10-14
    "Độ trễ đọc trực tiếp",
    "Đang hoạt động", "Đang chờ", "Tắt", "Lỗi", "Đã tắt", "Rảnh", "Đang khởi động",                    # 16-22
    "Đã tạm dừng khi dùng pin",
    "Chọn một ổ đĩa trong Cài đặt", "Thêm trò chơi ở tab Trò chơi",
    "Đang chờ trò chơi khởi động", "Đang chờ cửa sổ trò chơi được lấy nét",
    "Đã giữ thức", "Phiên", "Số lần khựng đã ghi", "Đã bật",                                           # 28-31
    "Chưa ghi nhận lần khựng nào.",
    "Mỗi điểm là lần đọc chậm nhất trong giây đó. Các đỉnh vượt đường đỏ là những lần khựng: lúc ổ đĩa do dự.",
    "Hãy mở một trò chơi (hoặc chọn “Luôn bật”) để xem độ trễ trực tiếp.",
    "Đang chờ dữ liệu...",
    "lần khựng", "bây giờ", "Có bản cập nhật", "Tải xuống",                                            # 36-39
    "Phát hiện trò chơi đã cài", "Đang quét...", "Thêm chương trình đang chạy…",
    "hoặc nhập tên chương trình, ví dụ game.exe",
    "Thêm", "Ổ đĩa", "Cường độ", "Mặc định",                                                           # 44-47
    "Chưa có trò chơi nào.\nNhấp “Phát hiện trò chơi đã cài” để tự động tìm.",
    "Chọn một chương trình đang chạy", "Hãy mở trò chơi của bạn trước, rồi chọn nó ở đây.",
    "Tìm kiếm...", "Không tìm thấy gì", "Trò chơi được phát hiện", "Không tìm thấy trò chơi mới.",      # 51-54
    "Đã tìm trong Steam, Epic Games và GOG. Bạn vẫn có thể thêm trò chơi bằng “Thêm chương trình đang chạy” hoặc nhập tên exe của nó.",
    "Chọn các trò chơi để giữ ổ đĩa luôn thức.",
    "Tên chương trình chỉ là phỏng đoán: hãy kiểm tra nếu trò chơi không kích hoạt.",
    "Chọn tất cả", "Thêm mục đã chọn", "Đóng",                                                         # 58-60
    "Ổ đĩa cần kiểm tra", "Làm mới", "Khởi động lại với quyền quản trị", "Đang đọc thông tin ổ đĩa...",
    "Những gì Windows biết về ổ đĩa này, kèm lời khuyên dễ hiểu.",
    "Sức khỏe", "Nhiệt độ", "Độ hao mòn", "Thời gian bật", "không có",                                 # 66-70
    "Còn trống {free} GB trên {total} GB",
    "Đo thời gian lần đọc đầu tiên sau khi ổ đĩa nhàn rỗi, có và không có giữ thức, rồi chọn thiết lập nhẹ nhất mà có ích. Mất khoảng 2 phút. Đừng chạy trò chơi trong lúc này.",
    "Chạy tự động tinh chỉnh", "Đang chuẩn bị…", "Hủy", "Đã hủy.", "Kiểm tra thất bại",                # 73-77
    "Giữ thức", "ms trung bình", "ms p95", "ms tối đa", "Không",                                       # 78-82
    "Giữ thức loại bỏ các lần khựng khi nhàn rỗi. Thiết lập khuyến nghị: {p}.",
    "Không phát hiện lần khựng nào khi nhàn rỗi trên ổ đĩa này: nó thức dậy nhanh. Giữ thức có lẽ không giúp ích ở đây.",
    "Ổ đĩa này do dự sau khi nhàn rỗi, nhưng giữ thức không giúp rõ rệt. Nguyên nhân có thể ở nơi khác: hãy thử Kiểm tra lag.",
    "Dùng {p} làm mặc định", "Đã lưu.",                                                                # 86-87
    "Hãy chuyển sang trò chơi ngay sau khi nhấn Bắt đầu. Sau 10 giây, Diskuick theo dõi ổ đĩa, CPU và bộ nhớ thật của bạn trong 30 giây và cho biết điều gì có vẻ bất ổn.",
    "Bắt đầu kiểm tra lag", "Bắt đầu sau {s} giây: hãy chuyển sang trò chơi ngay…", "Đang đo… hãy tiếp tục chơi",
    "Chỉ mang tính tham khảo: không đo mạng.",
    "Chỉ khi chơi game", "Luôn bật",                                                                   # 93-94
    "Tự động bắt đầu khi một trò chơi của bạn mở và dừng khi nó đóng. Thêm trò chơi ở tab Trò chơi.",
    "Chạy suốt thời gian Diskuick đang mở. Đơn giản, nhưng giữ ổ đĩa bận ngay cả khi nhàn rỗi.",
    "Ổ đĩa cần giữ thức",
    "Mức độ kích ổ đĩa. Các trò chơi có thể ghi đè mục này.",
    "Nhẹ", "Cân bằng", "Mạnh",                                                                         # 99-101
    "Các lần đọc ngẫu nhiên rất nhỏ, khoảng 10 lần mỗi giây. Tốn ít nhất: hãy thử cái này trước.",
    "Các lần đọc tuần tự nhẹ, khoảng 20 lần mỗi giây. Dành cho ổ đĩa cần thêm một chút.",
    "Đọc liên tục. Hiệu quả mạnh nhất, nhưng ổ đĩa luôn bận.",
    "Số giây giữa các lần đọc (nâng cao)", "mặc định",                                                 # 105-106
    "Nhập một số dương, hoặc để trống để dùng mặc định.",
    "Tạm dừng khi dùng pin", "Laptop: không giữ ổ đĩa bận khi rút sạc.",
    "Chỉ khi trò chơi đang được lấy nét", "Tạm dừng khi bạn Alt+Tab ra khỏi trò chơi.",
    "Thông báo khi trò chơi bắt đầu", "Một thông báo nhỏ ở khay hệ thống.",
    "Khởi động cùng Windows", "Chạy âm thầm ở khay hệ thống khi đăng nhập.",
    "Giao diện", "Theo hệ thống", "Tối", "Giao diện sáng", "Ngôn ngữ",                                  # 116-120
    "Kiểm tra cập nhật",
    "Chỉ liên hệ với tên kho lưu trữ; không gửi gì về bạn.",
    "Việc kiểm tra cập nhật tắt cho đến khi thiết lập kho phát hành.",
    "Mở thư mục dữ liệu", "Mở nhật ký khựng",
    "Cường độ thông minh đang bật: nó chọn mức cho bạn. Hãy tắt để tự chọn.",
    "Thông minh",                                                                                      # 127
    "Khởi động lại với quyền quản trị để quét nhanh",
    "Cho thấy thứ gì đang chiếm dung lượng, lớn nhất trước. Ở đây không có gì bị thay đổi hay xóa. Chạy với quyền quản trị sẽ đọc trực tiếp bảng tệp của ổ đĩa (như WizTree) chỉ trong vài giây; nếu không, nó đọc từng thư mục một, có thể mất một hai phút.",
    "Mất {s} giây.", "Đổi tên trò chơi", "Tên hiển thị cho",                                           # 130-132
    "Lớp phủ độ trễ",
    "Một bảng hiển thị trực tiếp nhỏ ở góc màn hình khi ổ đĩa đang được giữ thức (có trò chơi đang chạy, hoặc Luôn bật). Đây là một cửa sổ riêng, không bao giờ chạm vào trò chơi, và hiện trên các trò chơi dạng cửa sổ và không viền. Nó không thể hiện trên chế độ toàn màn hình độc quyền (ví dụ Battlefield 3): hãy chuyển trò chơi đó sang không viền hoặc dạng cửa sổ.",
    "Hiện lớp phủ khi trò chơi đang chạy", "Vị trí", "Xem trước",                                      # 135-137
    "Trên cùng bên trái", "Trên cùng bên phải", "Dưới cùng bên trái", "Dưới cùng bên phải",
    "Cập nhật ngay", "Đang tải xuống… {p}%", "Cập nhật thất bại", "Thử lại", "Kiểm tra ngay",          # 142-146
    "Đang kiểm tra…", "Bạn đã dùng bản mới nhất.", "Không thể kiểm tra cập nhật.", "Có bản cập nhật: {v}",
    "Mở Diskuick", "Thoát", "Đang giữ thức ổ đĩa {d}:",                                                # 151-153
    "Không thể thay đổi cài đặt khởi động",
    "Các phiên gần đây", "Có phải do ổ đĩa? Tóm tắt các phiên chơi gần đây của bạn.",
    "Chưa ghi nhận phiên nào. Báo cáo sẽ xuất hiện khi trò chơi đóng.",
    "Lần đọc tệ nhất", "lần khựng", "đỉnh", "ping",                                                    # 158-161
    "Đánh dấu lag",
    "Nhấn Ctrl+Alt+L (hoặc dùng menu khay) ngay khi trò chơi bị lag. Diskuick lưu lại những gì máy tính đang làm vào lúc đó.",
    "Chưa đánh dấu lag nào.", "Đánh dấu lag ngay", "Đã đánh dấu lag", "Phiên đã kết thúc",              # 162-167
    "Đã đóng để giải phóng tài nguyên", "Cường độ thông minh",
    "Bắt đầu ở mức Nhẹ và chỉ tăng dần khi ổ đĩa còn khựng, rồi hạ xuống khi ổn định. Bỏ qua lựa chọn ở trên (thiết lập riêng của trò chơi vẫn được ưu tiên).",
    "Cảnh báo ổ đĩa", "Báo cho tôi khi ổ đĩa chơi game gần đầy hoặc không còn khỏe.",                     # 171-172
    "Phím tắt",
    "Ctrl+Alt+L đánh dấu một khoảnh khắc lag. Ctrl+Alt+O hiện hoặc ẩn lớp phủ.",
    "Hiện lớp phủ khi ổ đĩa đang được giữ thức",
    "Hiện cả mức tải CPU và GPU", "Hiện cả FPS",                                                       # 176-177
    "Cần PresentMon.exe nằm cạnh Diskuick.exe và Diskuick chạy với quyền quản trị.",
    "Kiểm tra mạng (tùy chọn)",
    "Kiểm tra xem internet của bạn có thể là nguyên nhân gây lag không. Nhập 1.1.1.1 để kiểm tra kết nối chung của bạn, hoặc địa chỉ máy chủ bạn chơi (:cổng là tùy chọn, mặc định là 443). Trong Kiểm tra lag (và khi bạn đánh dấu lag), Diskuick đo ping (máy chủ mất bao lâu để trả lời) và mất gói (các phản hồi không bao giờ đến), để bạn phân biệt sự cố mạng với sự cố ổ đĩa. Chỉ mở một kết nối bình thường, vài lần mỗi giây, và không gửi gì về bạn. Để trống để giữ tắt.",
    "Máy chủ", "Nhập tên máy chủ hoặc địa chỉ, có thể kèm :cổng.",
    "Chế độ chơi game (tùy chọn)",
    "Khi một trò chơi của bạn bắt đầu, lịch sự yêu cầu các chương trình này đóng lại (chúng vẫn có thể nhắc bạn lưu) và mở lại khi trò chơi kết thúc. Không có gì bị buộc đóng.",
    "Chưa chọn chương trình nào.", "Xóa", "Chương trình đó được bảo vệ và không thể đóng.",            # 185-187
    "Mở lại sau đó", "Đĩa", "Ổ đĩa cần phân tích", "Quét", "Dừng", "Đang dừng...", "Lên",             # 188-194
    "Tên", "Kích thước", "Tệp", "% của thư mục cha", "Mở trong Explorer", "Mở thư mục này tại đây",    # 195-200
    "Trình phân tích dung lượng đĩa",
    "Cho thấy thứ gì đang chiếm dung lượng, lớn nhất trước. Nó đọc từng thư mục một nên ổ đĩa lớn mất một hai phút. Ở đây không có gì bị thay đổi hay xóa.",
    "Nhấn Quét để bắt đầu.", "Hãy quét một ổ đĩa để xem bản đồ của nó ở đây.",                        # 203-204
    "Đang quét {drive}: ...", "Đang quét {drive}: đến nay {files} tệp, {size}",
    "Tìm thấy {size} trong {files} tệp và {folders} thư mục.", "Ổ đĩa đã dùng: {used}.",
    "Đã dừng sớm nên đây chỉ là kết quả một phần.",
    "Một số thư mục được bảo vệ; hãy chạy với quyền quản trị để bao gồm chúng.",
    "Loại tệp", "Những loại tệp nào chiếm nhiều dung lượng nhất trên ổ đĩa này.",                       # 211-212
    "Dọn dẹp đĩa",
    "Chỉ xóa phần còn sót lại an toàn và có thể tạo lại: tệp tạm, bộ nhớ đệm và báo cáo sự cố. Tệp của bạn không bao giờ bị đụng đến. Hãy đánh dấu mục muốn dọn, kiểm tra kích thước, rồi dọn dẹp.",
    "Kiểm tra kích thước", "Đang kiểm tra kích thước...", "Dọn mục đã chọn", "Đang dọn dẹp...",         # 215-218
    "Hãy đánh dấu ít nhất một mục trước.", "Các mục đã đánh dấu sẽ giải phóng khoảng {size}.",
    "Thùng rác sẽ được dọn vĩnh viễn.",
    "Xóa khoảng {size} khỏi:\n\n{names}{note}\n\nTiếp tục?",
    "Đã giải phóng {size} ({files} tệp). Các mục đang dùng đã bị bỏ qua.",
    "Tệp tạm", "Do các chương trình để lại trong thư mục Temp của bạn.",                               # 224-225
    "Tệp tạm của Windows", "Thư mục Temp riêng của Windows. Chạy với quyền quản trị để dọn hết.",
    "Bộ nhớ đệm hình thu nhỏ", "Explorer tạo lại bản xem trước ảnh khi cần.",
    "Tệp kết xuất sự cố và báo cáo lỗi", "Các tệp chẩn đoán từ chương trình bị treo.",
    "Bộ nhớ đệm trình duyệt", "Bộ nhớ đệm của Chrome, Edge và Brave. Các trang tải chậm hơn một chút một lần.",
    "Bộ nhớ đệm shader", "Bộ nhớ đệm shader của GPU. Trò chơi có thể khựng ngắn ở lần khởi động tới trong lúc chúng được tạo lại.",
    "Thùng rác", "Xóa vĩnh viễn những gì có trong Thùng rác.",
    "Chuyển vào Thùng rác", "thư mục", "tệp",                                                          # 238-240
    "Chuyển {kind} này vào Thùng rác?\n\n{path}\n{size}\n\nBạn có thể khôi phục từ Thùng rác.",
    "Đang chuyển vào Thùng rác...",
    "Không thể chuyển vào Thùng rác (đang dùng, được bảo vệ hoặc đã hủy).",
    "Đã chuyển {size} vào Thùng rác. Hãy quét lại để làm mới các loại tệp.",
    "Quét nhanh (bảng tệp NTFS).",
    "Hãy chạy Diskuick với quyền quản trị để quét nhanh hơn nhiều.",
    "Thư mục", "Còn trống",                                                                           # 246-247
    "vd: 1.1.1.1",
))
