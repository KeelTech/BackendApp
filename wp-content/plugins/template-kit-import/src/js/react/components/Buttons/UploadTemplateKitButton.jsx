import React, { useState } from 'react'
import { withRouter } from 'react-router'
import styles from './UploadTemplateKitButton.module.scss'
import uploadTemplateKitZipFile from '../../api/uploadTemplateKitZipFile'
import ButtonIconAndLabel from './ButtonIconAndLabel'
import ButtonElement from './ButtonElement'
import { getImportedKitUrl } from '../../utils/linkGenerator'

export const DoTheFileUpload = ({ chosenFile, onSuccess }) => {
  const { loading, data, error } = uploadTemplateKitZipFile({ file: chosenFile })

  if (!loading && !error && data && data.templateKitId) {
    setTimeout(() => {
      onSuccess(getImportedKitUrl({ importedTemplateKitId: data.templateKitId }))
    }, 200)
  }

  return null
}

const UploadTemplateKitButton = ({ history }) => {
  const [chosenFile, setChosenFile] = useState(null)

  return (
    <>
      <ButtonElement element='label' htmlFor='upload-template-kit-zip-file'>
        <ButtonIconAndLabel label={chosenFile ? 'Processing...' : 'Upload Template Kit (Zip File)'} icon='link' />
        <input
          type='file'
          name='upload-template-kit-zip-file'
          id='upload-template-kit-zip-file'
          className={styles.formInput}
          onChange={e => {
            setChosenFile(e.target.files[0])
          }}
        />
      </ButtonElement>
      {chosenFile ? (
        <DoTheFileUpload
          chosenFile={chosenFile}
          onSuccess={(redirectUrl) => {
            setChosenFile(false)
            history.push(redirectUrl)
          }}
        />
      ) : null}
    </>
  )
}

export default withRouter(UploadTemplateKitButton)
