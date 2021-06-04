import React from 'react'
import Modal from 'react-modal'
import ModalEnvatoIcon from './ModalEnvatoIcon'
import styles from './MagicModalWrapper.module.scss'
const customStyles = {
  overlay: {
    backgroundColor: 'rgba(32, 32, 32, 0.81)',
    zIndex: 199999,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  content: {
    background: '#f1f1f1',
    border: '0',
    padding: '0',
    right: 'auto',
    bottom: 'auto',
    top: 'auto',
    left: 'auto',
    borderRadius: '4px'
  }
}

const MagicModalWrapper = ({ photoId, photoTitle, onCloseCallback = null, children }) => {
  const [modalIsOpen, setModalIsOpen] = React.useState(true)
  const closeModal = () => {
    setModalIsOpen(false)
    if (onCloseCallback) {
      onCloseCallback()
    }
  }

  // Make sure to bind modal to your appElement (http://reactcommunity.org/react-modal/accessibility/)
  // We get window.templateKitImport.modalAppHolder from our initial render in main.jsx:
  if (typeof window !== 'undefined' && window.templateKitImport && window.templateKitImport.modalAppHolder) {
    Modal.setAppElement(window.templateKitImport.modalAppHolder)
  }

  return (
    <Modal
      isOpen={modalIsOpen}
      onRequestClose={closeModal}
      style={customStyles}
      contentLabel='Envato Elements'
      data-testid='modal-wrapper'
    >
      <div className={styles.modalInner}>
        <div className={styles.modalHeader}>
          <div className={styles.modalLogo}>
            <ModalEnvatoIcon />
          </div>
          <div className={styles.headerNav} />
          <div className={styles.headerActions}>
            <button onClick={closeModal} data-testid='modal-close-button' className={styles.closeButton}>
              <span className={`dashicons dashicons-no-alt ${styles.dismissIcon}`} />
            </button>
          </div>
        </div>
        <div className={styles.magicModalInner}>
          {typeof children === 'function' ? children({ closeModal }) : children}
        </div>
      </div>
    </Modal>
  )
}

export default MagicModalWrapper
