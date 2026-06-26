import React from 'react';

export default function DeleteConfirmModal({ isOpen, onClose, onConfirm, isDeleting }) {
  if (!isOpen) return null;

  return (
    <div onClick={() => !isDeleting && onClose()} style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(8px)',
      WebkitBackdropFilter: 'blur(8px)',
      zIndex: 99999, display: 'flex', justifyContent: 'center', alignItems: 'center'
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: 'linear-gradient(135deg, #ffffff, #f0f9ff)',
        padding: '18px 20px',
        borderRadius: '18px',
        width: '85%',
        maxWidth: '270px',
        boxShadow: '0 15px 35px -10px rgba(14, 165, 233, 0.4)',
        border: '1px solid #bae6fd',
        textAlign: 'center',
        position: 'relative'
      }}>
        {/* Cloud Trash Icon */}
        <div style={{
          fontSize: '2.4rem',
          marginBottom: '8px',
          filter: 'drop-shadow(0 4px 8px rgba(239,68,68,0.25))'
        }}>
          ☁️🗑️
        </div>

        {/* Title */}
        <h3 style={{
          margin: '0 0 6px 0',
          color: '#0f172a',
          fontSize: '1.1rem',
          fontWeight: '800'
        }}>
          Xóa bình luận này?
        </h3>

        {/* Description */}
        <p style={{
          color: '#475569',
          fontSize: '0.82rem',
          lineHeight: '1.4',
          margin: '0 0 16px 0'
        }}>
          Bạn chắc chắn muốn xóa?<br/>
          <span style={{
            color: '#ef4444',
            fontSize: '0.78rem',
            fontWeight: '600',
            display: 'inline-block',
            marginTop: '4px'
          }}>
            ⚡ Không thể khôi phục
          </span>
        </p>

        {/* Buttons */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onConfirm}
            disabled={isDeleting}
            style={{
              flex: 1,
              padding: '8px 12px',
              background: 'linear-gradient(135deg, #ef4444, #dc2626)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontWeight: 'bold',
              fontSize: '0.85rem',
              cursor: isDeleting ? 'wait' : 'pointer',
              boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)',
              transition: 'all 0.2s',
              opacity: isDeleting ? 0.7 : 1
            }}
          >
            {isDeleting ? '⏳ Xóa...' : '🗑️ Xóa'}
          </button>
          <button
            onClick={onClose}
            disabled={isDeleting}
            style={{
              flex: 1,
              padding: '8px 12px',
              background: 'linear-gradient(135deg, #e0f2fe, #bae6fd)',
              color: '#0369a1',
              border: 'none',
              borderRadius: '10px',
              fontWeight: 'bold',
              fontSize: '0.85rem',
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              boxShadow: '0 2px 8px rgba(186, 230, 253, 0.4)',
              transition: 'all 0.2s'
            }}
          >
            Hủy
          </button>
        </div>
      </div>
    </div>
  );
}
