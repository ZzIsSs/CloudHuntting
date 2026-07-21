/**
 * Tính giờ xuất phát mặc định dựa trên giờ hiện tại + thời gian khảo sát (offset).
 * @param {number} offsetHours - Số giờ offset từ trang Dò mây (mặc định = 0).
 * @returns {string} Giờ định dạng "HH:MM" (VD: "14:30").
 */
export function getSmartStartTime(offsetHours = 0) {
  const now = new Date();
  now.setHours(now.getHours() + offsetHours);

  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}
