import React from 'react'
import importSingleTemplate from '../../api/importSingleTemplate'
import ButtonActionProvider from '../Actions/ButtonActionProvider'
import Button from '../Buttons/Button'

/**
 *
 * @param templateKitId
 * @param templateId
 * @param existingImports
 * @param customActionHook
 * @param completeCallback
 * @param errorCallback
 * @returns {*}
 * @constructor
 */
const InsertTemplateToPage = ({ templateKitId, templateId, existingImports, customActionHook = null, completeCallback = null, errorCallback = null }) => {
  const InsertingButton = <Button type='primary' label='Inserting...' icon='updateSpinning' disabled />
  return (
    <ButtonActionProvider
      DefaultButton={<Button type='primary' label='Insert Template' icon='plus' />}
      LoadingButton={InsertingButton}
      ErrorButton={<Button type='warning' label='Error' icon='cross' disabled />}
      SuccessButton={InsertingButton}
      CompletedButton={InsertingButton}
      actionHook={() => customActionHook ? customActionHook() : importSingleTemplate({ templateKitId, templateId, insertToPage: true })}
      isAlreadyCompleted={false}
      completedCallback={(data) => {
        if (data && data.imported_template_id) {
          if (completeCallback) {
            completeCallback(data)
          }
        }
      }}
      errorCallback={errorCallback}
    />
  )
}

export default InsertTemplateToPage
