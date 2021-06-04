import React from 'react'
import deleteTemplateKit from '../../api/deleteTemplateKit'
import ButtonActionProvider from '../Actions/ButtonActionProvider'
import Button from './Button'

/**
 * Helper to render a series of buttons to delete a template kit.
 *
 * @param templateKitId
 * @param customActionHook
 * @param completeCallback
 * @param errorCallback
 * @returns {*}
 * @constructor
 */
const DeleteTemplateKit = ({ templateKitId, customActionHook = null, completeCallback = null, errorCallback = null }) => {
  return (
    <ButtonActionProvider
      DefaultButton={<Button type='warning' label='' icon='trash' />}
      actionConfirmationMessage='Really delete this Template Kit?'
      LoadingButton={<Button type='warning' label='' icon='trash' disabled />}
      ErrorButton={<Button type='warning' label='' icon='trash' disabled />}
      SuccessButton={<Button type='warning' label='' icon='trash' disabled />}
      CompletedButton={<Button type='warning' label='' icon='trash' />}
      actionHook={() => customActionHook ? customActionHook() : deleteTemplateKit({ templateKitId })}
      isAlreadyCompleted={false}
      completedCallback={() => {
        if (completeCallback) {
          completeCallback()
        }
      }}
      errorCallback={errorCallback}
    />
  )
}

export default DeleteTemplateKit
