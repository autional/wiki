export interface Service {
  name: string;
  title: string;
  port: number;
}

export const services: Service[] = [
  { name: 'identity-service', title: '身份服务', port: 11001 },
  { name: 'profile-service', title: '用户资料服务', port: 11002 },
  { name: 'tenant-service', title: '租户服务', port: 11003 },
  { name: 'session-service', title: '会话服务', port: 11004 },
  { name: 'mfa-service', title: '多因素认证服务', port: 11005 },
  { name: 'oauth-service', title: 'OAuth 服务', port: 11006 },
  { name: 'wallet-service', title: '钱包服务', port: 11011 },
  { name: 'point-service', title: '积分服务', port: 11012 },
  { name: 'audit-service', title: '审计服务', port: 11013 },
  { name: 'notification-service', title: '通知服务', port: 11014 },
  { name: 'communication-service', title: '通信服务', port: 11015 },
  { name: 'storage-service', title: '存储服务', port: 11016 },
  { name: 'billing-service', title: '计费服务', port: 11017 },
  { name: 'compliance-service', title: '合规服务', port: 11018 },
  { name: 'status-service', title: '状态服务', port: 11019 },
  { name: 'secret-service', title: '密钥服务', port: 11020 },
  { name: 'saml-service', title: 'SAML 服务', port: 11021 },
  { name: 'pay-service', title: '支付服务', port: 11022 },
  { name: 'thirdparty-service', title: '第三方服务', port: 11023 },
  { name: 'verification-service', title: '身份验证服务', port: 11024 },
  { name: 'rbac-service', title: 'RBAC 服务', port: 11025 },
  { name: 'gateway-service', title: '网关服务', port: 11080 },
  { name: 'hash-service-standard', title: '密码哈希服务', port: 11026 },
  { name: 'hash-service-sm', title: '国密哈希服务', port: 11027 },
  { name: 'captcha3d-service', title: '3D 验证码服务', port: 11028 },
  { name: 'config-service', title: '配置中心服务', port: 11007 },
  { name: 'stream-service', title: '实时事件流服务', port: 11029 },
];

export const serviceByName = new Map(services.map(s => [s.name, s]));
