import React from 'react';
import { GoogleLogin } from '@react-oauth/google';

interface GoogleSignInButtonProps {
  onSuccess: (credentialResponse: any) => void;
  onError: () => void;
  text?: 'signin' | 'signup' | 'continue_with' | 'signin_with';
  shape?: 'rectangular' | 'pill' | 'circle' | 'square';
  theme?: 'outline' | 'filled_blue' | 'filled_black';
  size?: 'large' | 'medium' | 'small';
  width?: string;
}

const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({
  onSuccess,
  onError,
  text = 'signin_with',
  shape = 'rectangular',
  theme = 'outline',
  size = 'large',
  width = '384'
}) => {
  return (
    <div className="w-full flex justify-center">
      <GoogleLogin
        onSuccess={onSuccess}
        onError={onError}
        text={text}
        shape={shape}
        theme={theme}
        size={size}
        width={width}
        logo_alignment="left"
        auto_select={false}
        cancel_on_tap_outside={true}
      />
    </div>
  );
};

export default GoogleSignInButton;