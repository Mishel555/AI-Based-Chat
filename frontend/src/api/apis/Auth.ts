import client from '~/api/client';

interface ApiUserData {
  name: string;
  email: string;
  given_name: string;
  family_name: string;
  preferred_username: string;
  zoneinfo: string;
  email_verified: true;
}

export interface AuthApi {
  getUser: () => Promise<ApiUserData | { error: string }>;
}

export default (): AuthApi => ({
  async getUser() {
    try {
      const { data: response } = await client.get<ApiUserData>('auth/user');
      return response;
    } catch (error) {
      // @ts-ignore
      const { data, code } = error.response;
      return { error: data.error || '', code };
    }
  },
});
